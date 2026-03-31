# Blog Post Ideas

Ranked by impact: SEO value, hiring signal, virality potential, and uniqueness. Each one is a story you've already lived — no research needed, just write it.

---

## Tier 1 — Write These First (highest impact)

### 1. How We Rescued a Critical Government Project in One Week
When I joined Proline, I inherited a long-running government project in serious trouble. The server was being manually restarted 4 times a day, there were critical memory leaks everywhere, and the client had lost patience — the team had been disbanded. Within my first week, I traced and fixed the memory leaks, stabilized the system, and stopped the daily crashes. Over the next year, we redesigned the entire platform from scratch using microservice architecture with REST APIs, scaling to 60+ services managed by Kubernetes. The project went from near-cancellation to a success story.

**Why #1:** This is a hero story. Everyone has seen failing projects — few can say they fixed one in a week. High virality on LinkedIn/HN. Shows leadership, debugging skill, and architecture ability in one post.

**Keywords:** debugging, memory leaks, C++, architecture migration, microservices, leadership, Kubernetes

### 2. Building a Real-Time Bidding Engine for 1.5M Users and $100M Daily
I designed and built Turkey's national e-Auction platform for the Ministry of Trade. The system serves 1.5M+ registered users and processes approximately $100M+ in daily transaction volume. The core challenge was the real-time bidding engine — processing 1,000+ concurrent bids per auction while performing live balance checks, margin calculations, and ensuring financial consistency. Integrated with 4 major banks, e-Devlet (government identity), MERSIS, and MERNIS national registries. Built with .NET Core microservices architecture.

**Why #2:** System design content gets massive engagement. The scale ($100M/day, 1.5M users) makes it stand out. Great for SEO on "real-time bidding", "system design", "auction platform" keywords.

**Keywords:** system design, real-time, fintech, .NET Core, microservices, government scale

### 3. Lessons From Managing 10,000 Kubernetes Pods Across Continents
At intenseye, our AI workplace safety platform runs approximately 10,000 Kubernetes pods on Google Cloud, spanning data centers in the US, Europe, and Asia. This post covers the real challenges: multi-region deployment strategies, handling network latency between continents, rolling updates without downtime across a polyglot stack (Go, Kotlin, Scala, Python), observability with Prometheus at that scale, and the build system (Bazel + Pants + Buildkite) that makes it all deployable.

**Why #3:** "10K pods" is a number that gets clicks. Kubernetes content has huge SEO demand. Directly proves you operate at serious scale.

**Keywords:** Kubernetes, Google Cloud, multi-region, observability, Bazel, Buildkite, Prometheus

### 4. RTSP to WebRTC: Building a Custom Video Proxy by Compiling Chrome
At iSIM Platform, the challenge was rendering real-time video from thousands of ONVIF/RTSP cameras directly in the browser in a 4x4 grid layout. Standard WebRTC solutions couldn't handle it. My solution was to compile the Chrome engine from source, add custom API methods for camera stream conversion, and build a proxy layer that bridged RTSP to WebRTC natively. This enabled operators in a central command center to view live feeds from 5,000+ cameras across ~50 locations without plugins or latency.

**Why #4:** Extremely niche and technical — no one else has written this exact post. Video engineers will share it. Shows deep systems-level thinking.

**Keywords:** WebRTC, RTSP, Chromium, video engineering, browser internals, real-time streaming

---

## Tier 2 — Strong Follow-ups

### 5. Memory Leaks in C++ Video Systems: How to Find and Kill Them
A practical guide from the Proline trenches. The system was crashing daily with memory leaks so bad the server needed 4 manual restarts per day. How I used Valgrind, AddressSanitizer (ASAN), and custom memory tracking to find the leaks. Common patterns that cause leaks in video processing code: circular references in frame buffers, forgotten stream closures, exception paths that skip cleanup. With code examples.

**Why #5:** Evergreen SEO content. "C++ memory leak" gets thousands of monthly searches. Practical, code-heavy, helpful — the kind of post that ranks for years.

**Keywords:** C++, memory leaks, Valgrind, ASAN, debugging, video processing

### 6. From Monolith to 60 Microservices: A Practical Migration Playbook
The Proline migration wasn't just a rewrite — it was a cultural shift. This post covers the practical decisions: how we decomposed the monolith, chose ZeroMQ pub-sub for inter-service messaging, containerized with Docker, orchestrated with K8s, introduced Kafka for event streaming, and got buy-in from teams. Includes what went wrong (service boundaries we drew too early) and what worked (starting with the most painful module first).

**Why #6:** "Monolith to microservices" is a perennial hot topic. Practical, real-world migration stories always get engagement.

**Keywords:** monolith migration, microservices, ZeroMQ, Kafka, Docker, Kubernetes

### 7. Streaming 5,000 Cameras From 50 Locations Into One Platform
The iSIM Platform was deployed as a hybrid on-prem/cloud solution across approximately 50 different physical locations. Each location had different camera brands, different VMS software, different network configurations. The platform had to normalize all of these into a unified stream, enable live viewing and recording, and support operations like traffic violation processing from a central command center.

**Why #7:** IoT + video + scale = strong niche content. Good for SEO on "video streaming architecture", "multi-site surveillance".

**Keywords:** IoT, hybrid cloud, video streaming, multi-vendor, system architecture

### 8. AI Video Analytics Pipeline: DeepStream + TensorRT in Production
How intenseye processes millions of video frames daily using NVIDIA DeepStream and TensorRT for real-time AI inference. Covers the pipeline: video ingestion → frame extraction → GPU inference → alert generation. I implemented the initial DeepStream integration, handling model loading, batch processing, and output parsing. The system runs on both x86 data center GPUs and ARM-based Jetson edge devices.

**Why #8:** AI/ML + video is hot. NVIDIA DeepStream content is scarce — this could rank #1 for those search terms.

**Keywords:** DeepStream, TensorRT, NVIDIA, GPU inference, computer vision, edge AI

---

## Tier 3 — Niche but Valuable

### 9. 120 Cameras, One System: Building a High-Performance Native VMS
At InfoDif, we built a VMS from scratch in C++ with Qt that could handle 120+ simultaneous live camera streams with real-time viewing, recording, and video analytics. The challenges were pure performance engineering: thread management, memory pools for frame buffers, FFmpeg decoding pipelines, and keeping the UI responsive while processing gigabytes of video data per second.

**Keywords:** C++, Qt, FFmpeg, threading, performance engineering, video management

### 10. Real-Time Radar-PTZ Camera Synchronization for Threat Detection
In defense projects at InfoDif, we synchronized radar projection overlays with PTZ cameras — when radar detected a target, the system automatically calculated the azimuth and elevation, directed the PTZ camera to that position, and started tracking. The video analytics module would then classify the threat and trigger alerts.

**Keywords:** sensor fusion, radar, PTZ, defense, signal processing, real-time

### 11. Building a Polyglot Monorepo: Go + Kotlin + Python + Scala
At intenseye, the entire codebase lives in a monorepo with 4 languages, each with its own build system. Bazel handles Go and protocol buffers, Pants manages Python with CUDA-aware resolves across x86 and ARM, and SBT builds the Scala/Play backend. Buildkite orchestrates it all with GPU-aware CI agents.

**Keywords:** monorepo, Bazel, Pants, Buildkite, polyglot, CI/CD, developer experience

### 12. Temporal for Workflow Orchestration in Video Analytics
Why we chose Temporal over cron jobs and message queues for complex, long-running workflows. Covers our use cases: GPU-powered alert processing workers, video export pipelines, and multi-step data enrichment flows.

**Keywords:** Temporal, workflow orchestration, distributed systems, video analytics

### 13. NAT Traversal for P2P Video: UPnP and Hole Punching in Practice
At Ekin Technology, remote video surveillance required getting live RTSP streams through corporate firewalls and NAT routers without asking customers to configure port forwarding. I implemented a combination of UPnP device discovery, UDP hole punching, and a TURN-like relay fallback.

**Keywords:** NAT traversal, P2P, UPnP, hole punching, RTSP, networking

### 14. Design Patterns in C++: Real-World Examples From Video Processing
Based on my open-source DesignPatterns repo. Not academic examples — actual patterns I used in production video systems: Factory for codec selection, Singleton for hardware device managers, Composite for multi-stream pipelines, Decorator for filter chains.

**Keywords:** C++, design patterns, factory, singleton, open source

### 15. e-Arsiv: Building a Java Library for Turkish E-Invoice API
When I needed to integrate with Turkey's e-Archive (electronic invoice) system, there was no Java library available — only implementations in other languages. So I built one from scratch and open-sourced it. This post covers reverse-engineering the government API, handling XML/SOAP quirks, and why open-sourcing niche tools creates outsized value.

**Keywords:** Java, open source, API integration, e-invoice, Turkish government

---

## Tier 4 — Side Projects & Personal

### 16. Building an IP Protection Platform: EserTescil Architecture
How I built esertescil.com — a SaaS platform that lets creators protect their intellectual property using legally recognized timestamp certificates under Turkish law (Law No. 5070). The architecture: ASP.NET Core backend, React Native mobile app, file hashing without storing originals, integration with BTK-authorized timestamp authorities. From idea to revenue-generating product.

**Keywords:** SaaS, ASP.NET Core, React Native, legal tech, entrepreneurship

### 17. Kalman Filtering for GPS Speed: How Velox Achieves Sub-Second Response
Smartphone GPS updates at 1Hz — too slow for a real-time speedometer. Velox fuses 1Hz GPS with 10Hz accelerometer data using a Kalman filter to achieve near-instant speed response. This post explains the math, the Swift/CoreLocation/CoreMotion implementation, and the tradeoffs between accuracy and responsiveness.

**Keywords:** Kalman filter, sensor fusion, iOS, Swift, CoreLocation, GPS

### 18. Building a Campus Life Platform From Scratch
OnlyCampus: a full-stack mobile platform for university students — Spring Boot backend, React Native apps, WebSocket real-time chat, marketplace, roommate matching, push notifications via FCM and SNS, RevenueCat subscriptions, and self-hosted Kubernetes infrastructure on Hetzner.

**Keywords:** Spring Boot, React Native, Kubernetes, full-stack, product development

### 19. My Journey: From Shell Scripts (2008) to 10K Pods (2025)
A career retrospective. Starting with Linux shell scripts out of curiosity in 2008, learning C++ and OOP in 2009, becoming an engineer in 2012, and progressing through defense, smart city, IoT, and AI video analytics.

**Keywords:** career, retrospective, software engineering

### 20. Building Side Projects While Working Full-Time
I run EserTescil, develop OnlyCampus, MindMate, and Velox — all while working full-time as a senior engineer. Time management, knowing when to ship vs. polish, choosing boring tech for side projects.

**Keywords:** side projects, entrepreneurship, productivity

### 21. From Turkey to Berlin: A Software Engineer's Relocation Story
Moving from Ankara to Berlin — work permit process, cultural differences in engineering teams, what's different about the German tech scene, and practical tips for engineers considering the move.

**Keywords:** relocation, Berlin, Germany, career

### 22. 3 Countries, 14 Years: What I Learned Working in Turkey, Qatar, and Germany
Different engineering cultures, different project scales, different ways of building software. Ankara defense projects vs. Doha smart city deployment vs. Berlin AI startup.

**Keywords:** international, career, engineering culture

### 23. The Tools I Actually Use Every Day in 2025
My actual daily stack: IntelliJ for Kotlin/Java, GoLand for Go, VS Code for Python, Claude Code for AI-assisted development, Cursor for quick edits. Terminal setup, Git workflow, how I context-switch between 4 languages daily in a monorepo.

**Keywords:** developer tools, productivity, workflow, AI-assisted development

---

## LinkedIn Post Ideas (short-form, for weekly posting)

These are NOT blog posts — they are 3-5 paragraph LinkedIn posts to stay visible in the feed:

1. "The hardest bug I ever fixed was a memory leak that crashed a government server 4 times a day..."
2. "What managing 10,000 Kubernetes pods taught me about simplicity..."
3. "I hold a patent for a Video Network Gateway System. Here's what I learned from the process..."
4. "We shipped NVIDIA edge devices to factories that can stop a production line in milliseconds when someone is in danger..."
5. "I compiled Chrome from source to solve a video streaming problem. Here's why..."
6. "5,000 cameras, 50 locations, one platform. The architecture behind it..."
7. "The one question I ask before choosing any technology for a new project..."
8. "From Ankara defense projects to Berlin AI startup — what changed and what didn't..."
9. "Why I build side projects (EserTescil, OnlyCampus, Velox) while working full-time..."
10. "The tools I can't live without in 2025: Claude Code, Cursor, and why AI-assisted development is not cheating..."

Post format: Hook (first line grabs attention) → Story (2-3 paragraphs) → Takeaway (what you learned) → Question (drives comments)

---

## Notes
- Start with Tier 1 blog posts (1-4) — one per week, done in a month
- Then one Tier 2 blog post per month
- One LinkedIn short post per week (from list above)
- Platform: post.hamuryen.com (Medium-based)
- Language: English (wider reach)
- Blog posts: 1,000-2,000 words
- LinkedIn posts: 200-500 words
- Include architecture diagrams in blog posts where possible
- Each blog post should link back to hamuryen.com for SEO
- Share blog posts on LinkedIn with a personal intro paragraph
- Cross-post to dev.to and Hashnode for extra reach
