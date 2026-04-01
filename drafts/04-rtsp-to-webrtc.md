# RTSP to WebRTC: How We Built a Custom Video Proxy by Compiling the Chrome Engine

*When Kurento couldn't handle our camera load, we compiled Chromium's WebRTC library from source and built our own minimal RTSP-to-WebRTC bridge in about ten days.*

---

Standard WebRTC solutions work great in demos. Ten cameras, no problem. Maybe fifty. But when you need to stream hundreds of live camera feeds from geographically distributed locations into a browser-based command center, "works in development" stops meaning anything pretty quickly.

We hit this wall at iSIM Platform, where we were building an on-premises monitoring and command center system. Cameras were spread across wide areas, connected over fiber networks to a central operations room, and operators needed to watch live feeds in real time, in a multi-camera grid, directly in the browser. No plugins, no desktop apps. Just a browser.

The core problem: RTSP is the standard protocol for IP cameras. Browsers don't speak RTSP. We needed to bridge that gap.

## Why WebRTC?

The platform already had a desktop VMS (Video Management System) client, a .NET thick client that operators had to install, update, and maintain at every workstation. For new customer deployments, we wanted to move to a browser-based client. No installs, no plugins, accessible from anywhere. Existing customers would keep running the desktop client, but everything going forward would be browser-native.

The most obvious shortcut would have been to play RTSP directly in the browser. Back then, the VLC browser plugin could technically handle RTSP streams. But VLC's plugin relied on NPAPI, a plugin architecture from the Netscape era that browsers were actively killing off. Chrome had already removed NPAPI support entirely in September 2015 with Chrome 45. Firefox followed in March 2017 with Firefox 52. By 2019, browser plugins were dead technology. And even when they worked, they were desktop-only. We needed something that ran on desktop and mobile, across Chrome, Firefox, and Edge, with zero installation. Plugins were a dead end.

So the real question was which streaming protocol to use natively in the browser. We looked at the main candidates:

**HLS** was the most widely supported option. But standard HLS carries **15 to 30 seconds of latency**. The protocol works by chopping video into segments (typically 6 to 10 seconds each), and the player has to download a full segment before it can start playing. For a surveillance command center where operators need to react to live events and control PTZ cameras, half a minute of delay makes the feed useless. Low-Latency HLS wasn't an option either. Apple didn't announce LL-HLS until WWDC in June 2019, and even after the announcement it took a long time before player support caught up.

**MPEG-DASH** had similar problems. Also segment-based, typically **15 to 45 seconds** of latency. Both HLS and DASH were designed for scalable video delivery to large audiences, where a few seconds of delay is acceptable. Surveillance is a different animal.

**WebRTC** operates at **200 to 500 milliseconds**. It was built for real-time communication. Instead of buffering seconds of video into segments, it sends packets the moment they're available, with minimal buffering (tens of milliseconds). When an operator is controlling a PTZ camera and needs instant visual feedback, or reacting to a live incident on screen, sub-second latency is not optional.

WebRTC was the only realistic choice. Our command center client was built in Angular, operators used Chrome, Firefox, or Edge, all with solid WebRTC support. The browser side was straightforward. The hard part was the server side: getting RTSP camera streams into WebRTC, and doing it reliably at scale.

## The First Attempt: Kurento

Kurento Media Server seemed like the right tool. Open-source, built on top of GStreamer, had WebRTC support, decent community around it.

Kurento's architecture revolves around **MediaPipelines** and **MediaElements**. You create a pipeline and connect elements to it. A `PlayerEndpoint` ingests RTSP, a `WebRtcEndpoint` outputs WebRTC, and media flows between them through GStreamer underneath. Each element has sink pads for input and source pads for output. When two connected elements use incompatible codecs, Kurento's internal **agnosticbin** module handles transcoding automatically. It's event-driven, and the abstraction layer makes it easy to prototype with.

Getting a basic demo working was fast. Create a pipeline, add a `PlayerEndpoint` with the camera's RTSP URL, create a `WebRtcEndpoint`, connect them, call `play()`, and you've got live video in the browser. A Node.js signaling server handles WebSocket communication between the browser and Kurento, exchanging SDP offers/answers and ICE candidates. The [kurento-trans-rtsp-to-webrtc](https://github.com/iamcxa/kurento-trans-rtsp-to-webrtc) project shows this exact pattern and served as a reference for our initial implementation.

We also used Kurento's **Room** feature for stream fan-out, which was critical for us. In a surveillance system, multiple operators often want to watch the same camera at the same time. Without fan-out, every operator viewing the same camera opens a separate RTSP connection to it. IP cameras have limited resources: embedded processors with constrained RAM and CPU, limited network interfaces. Most cameras can only handle a handful of concurrent RTSP connections before they start dropping streams or become unresponsive. With Kurento's Room, we opened a single RTSP connection to the camera and distributed the resulting WebRTC stream to multiple clients.

The prototype worked. Demo day went well.

Then we tried to scale it.

Under real load, with dozens of simultaneous streams and multiple operators viewing different camera groups, things fell apart. Each stream created its own GStreamer pipeline with its own elements, each spawning threads through GStreamer's task-based threading model. The agnosticbin's automatic transcoding, which felt convenient during development, turned into a CPU problem at scale. Every codec mismatch between a camera's output and what the browser expected triggered real-time transcoding that could pin an entire core. Jitter buffers filled faster than processing could drain them, leading to frame drops that cascaded across sessions.

The Room feature brought its own set of problems. Streams routed through Rooms would randomly die. An operator would be watching a camera feed and it would just freeze or go black. Other times a stream wouldn't start at all when connecting to a Room that already had viewers. We added reconnection logic, but it was a band-aid over a deeper instability. The more operators connected to the same Room, the worse it got.

Kurento's own published benchmarks give a sense of the ceiling: on an 8-vCPU, 15GB RAM instance, it tops out at roughly 18 users in 9 parallel 1:1 sessions. Community reports show CPU pinning at 100% with just 10 concurrent streams. We needed to handle hundreds.

We were close to pushing Kurento to production, but the instability was too risky for a customer deployment. We forked the source, made custom builds. Stripped features, tuned buffer sizes, tweaked the GStreamer pipeline configuration. It helped a bit, but not enough. The problem wasn't configuration, it was architectural. Kurento is a general-purpose media server: conferencing, recording, computer vision filters, mixing, MCU/SFU routing. We needed one thing. Take an RTSP stream in, push a WebRTC stream out. All the other machinery, the MediaElement abstraction, the automatic transcoding, the event system overhead, was weight we didn't need. The Kurento Room project itself is now [marked as unmaintained](https://github.com/Kurento/kurento-room) on GitHub.

## The Decision

At some point it clicked. We don't need a media server. We need a protocol bridge.

Kurento has hundreds of features. We used one. What if we built just that one ourselves? Something minimal that converts RTSP to WebRTC and does nothing else. No conferencing. No recording. No mixing. Just the conversion.

I was leading the platform's architecture at the time. The rest of the team, five or six engineers, was busy with other parts of the system: the command center UI, camera management, recording, integrations. I took on the RTSP-to-WebRTC bridge as a solo project and started digging into what it would actually take. Every path I explored led to the same place: Chromium's source code.

## Why Chromium?

In 2019, if you wanted to use WebRTC outside of a browser (in a native application, a server, a proxy) your options were thin. The WebRTC standard is implemented in browsers, and the reference implementation lives inside Chromium as **libwebrtc**, a C++ library.

There was no standalone WebRTC library you could just install and link against. Pion, a pure Go WebRTC implementation, had appeared in 2018 but was brand new and unproven in production. GStreamer's webrtcbin element had landed around the same time but was immature. Janus Gateway existed, but it was another full media server with all the overhead we were trying to escape.

The only reliable path to native WebRTC was to pull libwebrtc out of the Chromium source tree and compile it yourself.

## Building the Bridge

Getting libwebrtc to compile was a project on its own. Chromium's source tree is enormous. You start by cloning Google's `depot_tools`, then use `gclient sync` to pull down the source, which eats up 40+ GB of disk space. The build system is GN (for generating build files) and Ninja (for executing them), both Google's own tools. The documentation mostly assumes you're building all of Chromium, not trying to extract one library from it. Roughly one in seven commits to the WebRTC codebase introduces a build break, so picking the right revision matters. The whole compilation process can take hours depending on your machine.

It was frustrating, but once I got a clean libwebrtc build that I could link against in a C++ project, we had the same WebRTC stack that powers Chrome. The same ICE implementation, the same DTLS-SRTP encryption, the same PeerConnection API. That was worth the pain.

With libwebrtc compiled, the rest was plumbing:

**RTSP ingestion.** RTSP itself is just a signaling protocol. The actual video travels over RTP (Real-time Transport Protocol). Camera sends H.264 video, which gets split into NAL units (Network Abstraction Layer units, the fundamental packets of H.264), then wrapped in RTP packets for transport. Our proxy needed to connect to the camera over RTSP, receive the RTP stream, and extract the H.264 frames. We used an existing C++ RTSP/RTP library for this rather than implementing the protocol from scratch.

**WebRTC output.** Those H.264 frames went into libwebrtc's PeerConnection API. Since the cameras already output H.264 and browsers support it natively through WebRTC, we didn't need any transcoding. The frames passed through without re-encoding. libwebrtc handled everything else: ICE negotiation for NAT traversal, DTLS handshake for key exchange, SRTP encryption for the media stream. All the complexity that makes WebRTC work across networks was handled by the library.

**Signaling.** A lightweight WebSocket server so browsers could request a specific camera stream, send an SDP offer, and get an answer back. Simple request-response, nothing fancy.

**Fan-out.** This was the piece that Kurento's Room had handled for us. The proxy maintained one RTSP connection per camera. When multiple operators requested the same camera, we fanned out the incoming frames to all their WebRTC peer connections. No duplicate connections to the camera, no wasted bandwidth on the camera's network interface. One ingest, many viewers.

**Nothing else.** No transcoding. No recording. No mixing. No filters. Every feature we didn't build was CPU we didn't burn.

The first working version was ready in about ten days. Rough around the edges, but it worked and it was fast.

## In Production

A single proxy pod could handle **128 concurrent camera streams**, a number Kurento never came close to. Need more? Scale the pods horizontally in Kubernetes. CPU usage was predictable and proportional to the number of active streams. No random spikes, no buffer overflows cascading into frame drops, no streams going dead like we'd seen with Kurento's Rooms.

Operators in the command center had a pool of hundreds of cameras and a configurable grid layout, from a single camera full-screen up to a 4x4 grid with 16 simultaneous streams. They'd drag a camera from the list into any cell, and the live stream would start rendering within a second. Pull it out, drag another one in. Instant. The experience matched what operators knew from the desktop VMS, except now it ran in a browser tab.

The whole thing was on-premises. No cloud. Each customer site had its own Kubernetes cluster running on local hardware, and the proxy ran as a workload inside it. RTSP traffic never left the local network, which kept latency low and eliminated any dependency on internet bandwidth. When a new site came on, we deployed the proxy into their cluster and pointed the cameras at it. Didn't matter what brand or model the cameras were. If they spoke RTSP and output H.264, they worked.

## The Landscape Today

If I were solving this same problem today, I would not touch Chromium's source code. The ecosystem caught up.

**Pion** has matured into a solid, production-grade WebRTC library for Go. It's the same kind of building block libwebrtc was for us, but instead of downloading half the internet and fighting C++ build systems, you write Go and run `go build`. Done.

**MediaMTX** and **go2rtc** are ready-to-use servers built on top of Pion. They do exactly what we built: RTSP in, WebRTC out. Single binary, zero dependencies. MediaMTX runs in Kubernetes with clustering support. go2rtc is lighter and popular in the home automation world. Both work.

**WHIP/WHEP** (WHIP became [RFC 9725](https://datatracker.ietf.org/doc/rfc9725/) in 2025) standardized WebRTC signaling over plain HTTP. The custom WebSocket signaling layer we had to design is now a two-request HTTP handshake defined in an RFC.

What took us ten days to build from Chromium source is now a config file and a binary download.

But in 2019, none of this existed. Compiling Chromium's WebRTC library and writing a minimal bridge around it was the right call. Sometimes the best engineering decision is recognizing that the tool you need hasn't been built yet, and building just enough of it yourself.

## What I Took Away From This

**Try the existing tools first.** We started with Kurento. That was the right call. You don't build custom infrastructure until you've actually proven that what's out there can't do the job. But when it can't, stop patching and recognize the mismatch.

**Scope is the multiplier.** Kurento didn't fail because it's bad software. It failed for us because it's a general-purpose media server and we needed a single-purpose protocol bridge. The features we never touched were actively costing us CPU and stability. When you build your own thing, fight the urge to add features. Every feature you skip is complexity you don't maintain.

**Ecosystems move faster than you think.** What required compiling Chromium from source in 2019 is a Go binary today. What was bleeding edge back then (Pion, WHIP) is now an IETF standard. Build what you need now, but don't assume your custom solution needs to live forever. Today MediaMTX does what our proxy did, probably better, and it's open source.

**Recognize when the tools don't exist yet.** In 2019, there was no production-ready, lightweight RTSP-to-WebRTC bridge. Spending weeks evaluating half-baked options would have been wasted time. Recognizing this early and committing to building our own saved us from that trap.

---

## Further Reading

**WebRTC Native Development:**
- [WebRTC Native Code Development](https://webrtc.github.io/webrtc-org/native-code/development/)
- [Understanding libwebrtc](https://dyte.io/blog/understanding-libwebrtc/)
- [Making WebRTC source building not suck](https://webrtchacks.com/building-webrtc-from-source/)

**RTSP and RTP:**
- [RFC 6184: RTP Payload Format for H.264 Video](https://datatracker.ietf.org/doc/html/rfc6184)

**Modern Alternatives:**
- [MediaMTX](https://github.com/bluenviron/mediamtx)
- [go2rtc](https://github.com/AlexxIT/go2rtc)
- [Pion WebRTC](https://github.com/pion/webrtc)

**Signaling Standards:**
- [RFC 9725: WHIP (WebRTC-HTTP Ingestion Protocol)](https://datatracker.ietf.org/doc/rfc9725/)
- [WHEP Draft: WebRTC-HTTP Egress Protocol](https://datatracker.ietf.org/doc/draft-ietf-wish-whep/)

**Streaming Protocol Comparisons:**
- [WebRTC Latency: Comparing Low-Latency Streaming Protocols](https://www.nanocosmos.net/blog/webrtc-latency/)
- [LL-HLS, CMAF, and WebRTC: Which Is Best?](https://cloudinary.com/guides/live-streaming-video/low-latency-hls-ll-hls-cmaf-and-webrtc-which-is-best)
- [Introducing Low-Latency HLS (WWDC 2019)](https://developer.apple.com/videos/play/wwdc2019/502/)

**Background:**
- [Kurento Media Server Documentation](https://doc-kurento.readthedocs.io/)
- [Kurento RTSP to WebRTC reference implementation](https://github.com/iamcxa/kurento-trans-rtsp-to-webrtc)
- [Kurento Room (unmaintained)](https://github.com/Kurento/kurento-room)
- [GStreamer WebRTC](https://gstreamer.freedesktop.org/documentation/webrtc/index.html)
- [NPAPI Deprecation (Chromium)](https://www.chromium.org/developers/npapi-deprecation/)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience in distributed systems, real-time video, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
