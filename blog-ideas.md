# Articles and Upcoming Topics

Engineering essays by [Burak Hamuryen](https://hamuryen.com) on video infrastructure, native code, build systems, and reliable backends.

## Scheduled for October 10–14, 2026

Scheduled on Medium for 10:00 Europe/Berlin (UTC+2), verified on October 9. Captions, alt text, five topics per story and custom SEO metadata are saved. See [publication manifest](drafts/medium/publication-manifest.json).

| Day | Article | Supporting material | Cover |
|---|---|---|---|
| Saturday, October 10 | [Python 3.15 Lazy Imports: Where the Startup Cost Goes](drafts/20-python-315-backend-faster.md) | Same-runtime lazy-import experiment, 120 observations, raw results and reproducible script | [Image](drafts/assets/python315-lazy-imports-cover.png) |
| Monday, October 12 | [When Is Self-Hosting AI Actually Cheaper?](drafts/21-when-is-self-hosting-ai-cheaper.md) | Explicit assumptions, executable cost model, capacity and API-price sensitivity | [Image](drafts/assets/self-hosting-ai-cost-cover.png) |
| Wednesday, October 14 | [Your Kafka Consumers Are Becoming a Workflow Engine](drafts/22-kafka-consumers-workflow-engine.md) | Worked cancellation scenario, durable handoff, failure decisions, Kafka/DB/Temporal boundaries | [Image](drafts/assets/kafka-workflow-engine-cover.png) |

## New articles

| Article | Focus | Cover |
|---|---|---|
| [Before Buying More GPUs, Fix Your Video Pipeline](drafts/n2-before-buying-more-gpus-fix-your-video-pipeline.md) | Frame movement, buffer ownership, queues, and measuring useful capacity | [Image](drafts/assets/before-buying-more-gpus-cover.png) |
| [4 Years, 6 Languages, 1 Monorepo: What I'd Do Differently](drafts/11-four-years-six-languages-one-monorepo.md) | Integration across 20–30 services and components, test selection, Git, and releases | [Image](drafts/assets/four-years-six-languages-one-monorepo-cover.png) |
| [Your Camera Is Online. Is the Video Still Live?](drafts/s1-camera-online-video-live.md) | Stream progress, measurable delay, playback, and recording health | [Image](drafts/assets/camera-online-video-live-cover.png) |
| [AI Agents Are Distributed Systems. Treat Them Like One.](drafts/t11-ai-agents-are-distributed-systems.md) | Lost responses, retries, idempotency, and durable work | [Image](drafts/assets/ai-agents-distributed-systems-cover-v2.png) |

## More articles

- [How We Rescued a Critical Government Project in One Week](drafts/01-rescued-government-project.md)
- [The C++/CLI Destructor Trap: Why Your Native Wrapper Is Leaking Memory](drafts/02-cpp-cli-disposable-pattern.md)
- [~10,000 Kubernetes Pods, Mostly GPU: Lessons From Running AI Infrastructure Across Continents](drafts/03-10k-kubernetes-pods.md)
- [RTSP to WebRTC: How We Built a Custom Video Proxy by Compiling the Chrome Engine](drafts/04-rtsp-to-webrtc.md)
- [Building a National E-Auction Platform for 1.4 Million Users](drafts/05-national-auction-platform.md)
- [You Probably Don't Need Microservices](drafts/08-you-probably-dont-need-microservices.md)
- [From Monolith to 15 Microservices: When It Actually Made Sense](drafts/08b-from-monolith-to-15-microservices.md)
- [I Mined Bitcoin in 2012 on an NVIDIA Tesla GPU. Then a Hard Drive Died.](drafts/19-bitcoin-mining-2012-nvidia-tesla.md)
- [Every AI Config File Explained: What Goes Where and Why](drafts/a1-ai-config-files-explained.md)
- [What Actually Works When Coding with AI (And What Doesn't)](drafts/a2-what-works-coding-with-ai.md)
- [MCP Servers I Actually Use (And How to Set Them Up)](drafts/a3-mcp-servers-i-actually-use.md)
- [GitHub Will Train AI on Your Copilot Data by April 24. Here's How to Stop It.](drafts/t1-github-training-private-repos.md)

## Upcoming topics

### Video, recording, and native code

| Topic | Question |
|---|---|
| Your Video File Exists. Can You Play It After a Crash? | What must be finalized, flushed, and recovered before a recording is usable? |
| The Network Went Down. Did the Recording Continue? | How should local storage, reconnects, and delayed uploads work together? |
| One Slow Viewer Can Stall Your Video Pipeline | Where should consumer branches separate, and what happens when their queues fill? |
| The Stream Is Fast. Why Does the First Frame Take So Long? | How do keyframe timing and decoder configuration affect startup for a viewer joining an H.264 stream? [GStreamer reference](https://gstreamer.freedesktop.org/documentation/rtp/rtph264pay.html) |
| Your Deployment Succeeded. Your Streams Disconnected. | How do rollouts affect long-lived sessions and recovery time? |
| What Media over QUIC Changes for a Camera-to-Browser Pipeline | Which transport problems does a new protocol address, and which remain? |
| Who Owns This Frame? C++, Python, and the Cost of a Copy | How do ownership and buffer lifetime cross a language boundary? |
| Recovering a Video Export After a Restart | How can remuxing, transcoding, and upload resume without losing track of completed work? |
| NAT Traversal for P2P Video | What happens when endpoints cannot accept inbound connections? |
| Building a Native Video Management System | How do decoding, recording, and a responsive UI share finite resources? |
| Connecting Cameras Across Different Networks | How do protocol differences, reconnects, and recording access affect integration? |
| CUDA Rust Through the Eyes of a C++ Engineer | How do device-code tooling, memory ownership, and C++ interoperability fit together? |
| Finding Memory Leaks Across a Native Boundary | Which allocations outlive the wrappers that appear to own them? |

### Builds, languages, and backends

| Topic | Question |
|---|---|
| Same Dockerfile, Different CPU, Different Result | What changes when a service and its native dependencies move between amd64 and arm64? |
| When a Build Cache Reuses the Wrong Result | Which undeclared inputs make a cached output unsafe to reuse? |
| One Changed File. Which Tests Should Run? | How can dependency graphs select useful checks without missing downstream effects? |
| One DTO, Six Languages: Where Compatibility Breaks | How do missing fields, default values, enums, and 64-bit numbers behave across binary and JSON boundaries? [Protocol Buffers reference](https://protobuf.dev/programming-guides/json/) |
| Free-Threaded Python Meets a C++ Extension | What happens to shared native state when Python threads can run concurrently? |
| The HTTP Request Ended. The Work Didn't. | How should cancellation and deadlines reach downstream work? |
| What Happens When Two Bids Arrive at the Same Time? | Which guarantees belong in transactions, constraints, and retry handling? |
| The Architecture I Chose for My Own Product | Which boundaries are useful before a product needs a large platform? |
| Building a Java Client for an E-Invoice API | How should a client handle schema changes, errors, and external service behavior? |

### AI-assisted development and software maintenance

| Topic | Question |
|---|---|
| Reopening My Old Video Streaming Code With an AI Coding Agent | How can a small maintenance change be reviewed against real streaming behavior? |
| Revisiting My C++ Design Patterns | Which abstractions still help when returning to an older codebase? |
| What to Tell AI Before It Changes Your Backend | Which contracts and failure expectations should be part of a coding task? |
| The Tests Pass. Would You Merge This AI-Generated PR? | What must review establish beyond a green test run? |
| The Tools I Use Across Languages | Which tools reduce the cost of switching between ecosystems? |

### Engineering careers

- From Shell Scripts to AI Infrastructure: My Engineering Journey
- From Turkey to Berlin: A Software Engineer's Relocation Story
- Working Across Turkey, Qatar, and Germany: Lessons in Engineering Culture
