# Blog Post Ideas

Ranked by impact: SEO value, hiring signal, virality potential, and uniqueness. Each one is a story you've already lived — no research needed, just write it.

---

## Tier 1 — Write These First (highest impact)

### 1. How We Rescued a Critical Government Project in One Week ✅
When I joined Proline, I inherited a long-running government project in serious trouble. The server was being manually restarted 4 times a day, there were critical memory leaks everywhere, and the client had lost patience — the team had been disbanded. Within my first week, I traced and fixed the memory leaks, stabilized the system, and stopped the daily crashes. Over the next year, we redesigned the entire platform from scratch using microservice architecture with REST APIs, scaling to 60+ services managed by Kubernetes. The project went from near-cancellation to a success story.

**Status:** Published on Medium.

**Keywords:** debugging, memory leaks, C++, architecture migration, microservices, leadership, Kubernetes

### 2. The C++/CLI Destructor Trap: Why Your Native Wrapper Is Leaking Memory ✅
Technical deep-dive companion to post #1. The exact C++/CLI pattern that caused the government project's memory leaks — missing `!Class` finalizer in native wrappers. With code examples, a checklist, and the pure C# equivalent pattern.

**Status:** Published on Medium.

**Keywords:** C++/CLI, memory leaks, .NET, IDisposable, finalizer, native interop

### 3. Lessons From Managing 10,000 Kubernetes Pods Across Continents ✅
At intenseye, our AI workplace safety platform runs approximately 10,000 Kubernetes pods on Google Cloud, spanning data centers in the US, Europe, and Asia. This post covers the real challenges: multi-region deployment strategies, handling network latency between continents, rolling updates without downtime across a polyglot stack (Go, Kotlin, Scala, Python), observability with Prometheus at that scale, and the build system (Bazel + Pants + Buildkite) that makes it all deployable.

**Status:** Published on Medium.

**Keywords:** Kubernetes, Google Cloud, multi-region, observability, Bazel, Buildkite, Prometheus

### 4. RTSP to WebRTC: Building a Custom Video Proxy by Compiling Chrome ✅
At iSIM Platform, the challenge was rendering real-time video from RTSP cameras directly in the browser. Kurento Media Server couldn't handle the load. Built a custom C++ RTSP-to-WebRTC bridge using libwebrtc compiled from Chromium source. Single proxy pod handled 128 concurrent streams. Deployed on-premises on Kubernetes.

**Status:** Published on Medium.

**Keywords:** WebRTC, RTSP, Chromium, video engineering, libwebrtc, Kurento, real-time streaming

---

## Tier 2 — Strong Follow-ups

### 5. Building a National E-Auction Platform for 1.4 Million Users ✅
The national customs liquidation auction platform. 1.4M users, 6B TL annual volume, last-second bidding chaos, auto-bid engine, bot attacks on launch day, bank SOAP integrations with daily reconciliation, e-Government OpenID authentication, real-time company authorization from national commercial registry.

**Status:** Published on Medium.

**Keywords:** system design, real-time, auction, .NET Core, WebSocket, Redis

**Keywords:** system design, real-time, fintech, .NET Core, microservices, government scale

### 7. Memory Leaks in C++ Video Systems: How to Find and Kill Them
A practical guide from the Proline trenches. The system was crashing daily with memory leaks so bad the server needed 4 manual restarts per day. How I used Valgrind, AddressSanitizer (ASAN), and custom memory tracking to find the leaks. Common patterns that cause leaks in video processing code: circular references in frame buffers, forgotten stream closures, exception paths that skip cleanup. With code examples.

**Why:** Evergreen SEO content. "C++ memory leak" gets thousands of monthly searches. Practical, code-heavy, helpful — the kind of post that ranks for years.

**Keywords:** C++, memory leaks, Valgrind, ASAN, debugging, video processing

### 8. You Probably Don't Need Microservices ✅
Contrarian take backed by real experience (60 microservices in production). CNCF survey: 42% consolidating back. Case studies: Segment (140 > 1), Amazon Prime Video (90% cost cut), Istio (rebuilt to single binary). Hidden costs: network latency, no FK/CASCADE/JOIN, saga hell, distributed debugging, infrastructure per service, testing complexity. Quotes from Sam Newman, Martin Fowler, Kelsey Hightower, DHH. Distributed monolith anti-pattern. Shopify's modular monolith alternative (Packwerk, 2.8M lines, 173B Black Friday requests). Resume-driven development test. When microservices actually make sense (multiple teams, different scaling, regulatory isolation).

**Status:** Draft ready. Scheduled for Medium.

**Keywords:** microservices, monolith, software architecture, distributed systems, Kubernetes

### 8b. From Monolith to 15 Microservices: When It Actually Made Sense ✅
2013, 3-person team, C++/Qt/gSOAP, 10-15 services before "microservices" was a word. No Docker, no K8s, CentOS systemd services. Previous monolithic client project taught domain boundaries. gSOAP namespace collision pain, shared PostgreSQL with separate schemas, on-premise deployment. What went right (clear boundaries, small team, right number), what went wrong (no service discovery, no centralized logging, gSOAP friction). Companion to #8.

**Status:** Draft ready. Scheduled for Medium.

**Keywords:** monolith migration, microservices, SOAP, REST, C++, gSOAP, software architecture

### 9. Streaming 5,000 Cameras From 50 Locations Into One Platform
The iSIM Platform was deployed as a hybrid on-prem/cloud solution across approximately 50 different physical locations. Each location had different camera brands, different VMS software, different network configurations. The platform had to normalize all of these into a unified stream, enable live viewing and recording, and support operations like traffic violation processing from a central command center.

**Why:** IoT + video + scale = strong niche content. Good for SEO on "video streaming architecture", "multi-site surveillance".

**Keywords:** IoT, hybrid cloud, video streaming, multi-vendor, system architecture

### 10. AI Video Analytics Pipeline: DeepStream + TensorRT in Production
How intenseye processes millions of video frames daily using NVIDIA DeepStream and TensorRT for real-time AI inference. Covers the pipeline: video ingestion → frame extraction → GPU inference → alert generation. I implemented the initial DeepStream integration, handling model loading, batch processing, and output parsing. The system runs on both x86 data center GPUs and ARM-based Jetson edge devices.

**Why:** AI/ML + video is hot. NVIDIA DeepStream content is scarce — this could rank #1 for those search terms.

**Keywords:** DeepStream, TensorRT, NVIDIA, GPU inference, computer vision, edge AI

---

## Tier 3 — Niche but Valuable

### 9. 120 Cameras, One System: Building a High-Performance Native VMS
At InfoDif, we built a VMS from scratch in C++ with Qt that could handle 120+ simultaneous live camera streams with real-time viewing, recording, and video analytics. The challenges were pure performance engineering: thread management, memory pools for frame buffers, FFmpeg decoding pipelines, and keeping the UI responsive while processing gigabytes of video data per second.

**Keywords:** C++, Qt, FFmpeg, threading, performance engineering, video management

### 10. Real-Time Radar-PTZ Camera Synchronization for Threat Detection
In defense projects at InfoDif, we synchronized radar projection overlays with PTZ cameras — when radar detected a target, the system automatically calculated the azimuth and elevation, directed the PTZ camera to that position, and started tracking. The video analytics module would then classify the threat and trigger alerts.

**Keywords:** sensor fusion, radar, PTZ, defense, signal processing, real-time

### 11. 4 Years, 4 Languages, 1 Monorepo: What I'd Do Differently
At intenseye, the entire codebase lives in a monorepo with Go, Kotlin, Python, and Scala. Bazel handles Go and protocol buffers, Pants manages Python with CUDA-aware resolves across x86 and ARM, SBT builds the Scala/Play backend. Buildkite orchestrates it all with GPU-aware CI agents. After 4+ years as a heavy monorepo user: what genuinely works (single source of truth, atomic cross-service changes, shared tooling), what hurts (build times, CI complexity, onboarding friction), and what I'd do differently. Honest take on when monorepo is the right call and when it's not worth the overhead.

**Why:** Monorepo content is either "Google does it so you should too" or "it's terrible." A balanced 4-year retrospective from someone who actually lived it is rare.

**Keywords:** monorepo, Bazel, Pants, Buildkite, polyglot, CI/CD, developer experience, git workflow

**Status:** Not started.

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

### 19. I Mined Bitcoin in 2012 on an NVIDIA Tesla GPU. Then a Hard Drive Died. ✅
Personal story. 2012, first job, Dell workstation with NVIDIA Tesla GPU, CUDA face recognition and license plate detection. Coworker introduces Bitcoin at $11. Mining for a few days, $4-5 earned. Left running over weekend. Monday: disk dead. $180 HDD purchase, $7-8 in pool (~0.7 BTC). Rage quit. $180 could have bought ~16 BTC (touched $140K since). Dry humor, self-deprecating, "timing was right, method was wrong."

**Status:** Draft ready. Scheduled for Medium.

**Keywords:** Bitcoin, GPU mining, NVIDIA Tesla, CUDA, cryptocurrency, personal story

### 20. My Journey: From Shell Scripts (2008) to 10K Pods (2025)
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

## AI-Assisted Development Series (3-post series, interlinked)

These three posts form a series. Each stands alone but links to the others. Target audience: developers using AI coding tools who want to go beyond basics. Tone: practical guide with real examples, not generic listicles.

### A1. Every AI Config File Explained: What Goes Where and Why ✅
CLAUDE.md, AGENTS.md, .cursorrules, settings.json, .claude/rules/, .mcp.json, skills, subagents. Quick reference table, CLAUDE.md vs AGENTS.md comparison, path-scoped rules, hooks for 100% enforcement, team setup, decision tree, Boris Cherny's 100-line approach. Auto memory and global setup (~/.claude/).

**Status:** Draft ready. Scheduled for Medium.

**Keywords:** CLAUDE.md, AGENTS.md, .cursorrules, Claude Code configuration, AI coding setup, settings.json, hooks

### A2. What Actually Works When Coding with AI (And What Doesn't) ✅
Plan-first workflow (Boris Tane, Osmani), context management (/clear, /compact, subagents), slash commands (/context, /cost, /diff, /plan, /rewind), breaking work into small pieces, tests first. AI failure patterns, METR study (19% slower), 80% problem, code review, honest downsides (babysitting, skill atrophy, joy loss).

**Status:** Draft ready. Scheduled for Medium.

**Keywords:** AI coding workflow, Claude Code tips, AI pair programming, prompt engineering, AI-assisted development

### A3. MCP Servers I Actually Use (And How to Set Them Up) ✅
CLI vs MCP rule (ScaleKit benchmark: 10-32x cheaper), servers kept (Context7, Sentry, Notion, Playwright, PostgreSQL), servers dropped (GitHub MCP, Filesystem, Memory, Sequential Thinking), .mcp.json config, building custom servers (FastMCP), security (30 CVEs in 60 days, ContextCrush, AgentSeal audit), org vs individual value (Pinterest case study).

**Status:** Draft ready. Scheduled for Medium.

**Keywords:** MCP servers, Model Context Protocol, Claude Code MCP, .mcp.json, AI tool integration

### Series Cross-Links
Add after all three are published (URLs needed). Reminder saved for ~2026-04-13.

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

## Trending Ideas (April 2026, research-backed)

These are based on what's actually trending on HN, Medium, dev.to, and Reddit right now. Ranked by viral potential.

### T1. GitHub Will Train AI on Your Copilot Data by April 24. Here's How to Stop It. ✅
What data is collected (prompts, code snippets, context, metadata), who is affected (Free/Pro/Pro+ yes, Business/Enterprise no), 30-second opt-out steps, GDPR "legitimate interest" problem (Berlin/EU perspective), Pro+ pricing gap ($39 but no enterprise protection), alternatives (Tabnine, Continue). 232 downvotes on GitHub's own discussion. 7 source links.

**Status:** Draft ready. Scheduled for Medium (April 11, 2026).

**Keywords:** GitHub Copilot, private repos, AI training, GDPR, data privacy, opt out

### T2. The Vibe Coding Hangover: What Actually Broke in Production
Vibe coding backlash is peak right now. Apple blocked vibe-coded app updates. Security test found 69 vulnerabilities across 15 vibe-coded apps. Code churn up 41%, duplication 4x. Write from perspective of senior engineer who actually uses Claude Code and Cursor on real distributed systems, not a think-piece writer. What happened to code quality over months of daily AI usage.

**Why it works:** #1 developer discourse topic, but no real production war stories exist. All hot takes, no data.
**Keywords:** vibe coding, AI coding tools, code quality, Claude Code, Cursor, AI-generated code
**Status:** Not started.

### T3. I Run 10,000 Kubernetes Pods. Here's Why Most Teams Should Use Something Simpler.
The "boring tech" movement is huge. "My 2026 Tech Stack is Boring as Hell" went viral. But all the monolith-return posts are from people who never ran K8s at scale. Write the "yes AND" post: I run 10K pods across continents, and even I think most teams shouldn't. When K8s is justified vs when a single server is enough.

**Why it works:** Contrarian from actual authority. Everyone else writing "K8s bad" never operated it at scale.
**Keywords:** Kubernetes, K8s alternatives, boring tech stack, cloud native, platform engineering
**Status:** Not started.

### T4. 67% of Developers Spend More Time Debugging AI Code. I Measured It in My Own Workflow.
Developer frustration with AI tools is massive undercurrent. 59% of engineering leaders report deployment problems from AI. But no one has published actual time-tracking data. Measure real AI tool ROI: time saved vs time debugging, by task type, over a month of daily use.

**Why it works:** Data-driven contrarian. Everyone claims AI makes them faster but METR study showed 19% slower. First-person measurement would be unique.
**Keywords:** AI coding productivity, developer productivity, AI tools ROI, Claude Code, Cursor
**Status:** Not started.

### T5. AI Writes 42% of Our Code But We Trust It for 0% of Critical Logic. Here's My Framework.
The "AI replacing developers" debate is at fever pitch. Fortune: "software engineers may not exist by year end." Meanwhile 95% of devs don't trust AI for mission-critical code. Write the nuanced middle: exactly which tasks to delegate to AI and which never, with a decision framework. C++, CUDA, distributed systems perspective where AI tools are weakest.

**Why it works:** Polarized debate needs a framework, not another hot take. Senior engineer with complex-domain experience is the right voice.
**Keywords:** AI replacing developers, AI coding trust, software engineering future, AI framework
**Status:** Not started.

### T6. Our GPU Cloud Bill Was 5x Our Compute Bill. Here's How We Cut It by 60%.
GPU/AI cost management is #1 desired FinOps skill in 2026. GPU instances cost 5-10x standard compute. Cloud waste hits $200B annually. H100 prices range $2.49/hr to $14.19/hr depending on provider (5.7x spread for same hardware). Write practitioner's guide, not consultant's guide.

**Why it works:** FinOps trending, GPU costs are the new pain point. Almost zero first-person engineering stories about optimizing GPU costs in production.
**Keywords:** GPU cloud costs, FinOps, NVIDIA, cloud cost optimization, AI infrastructure costs
**Status:** Not started.

### T7. Gemma 4 Runs on an iPhone. Here's What Edge AI Means for Backend Engineers.
Google launched Gemma 4 with on-device agentic capabilities. LiteRT-LM is new edge inference framework. Almost all edge AI content is written by ML engineers. Nothing from backend/infrastructure engineer perspective. Bridge cloud-native backend engineering and edge AI.

**Why it works:** Edge AI trending but all content is ML-focused. Backend engineer perspective is the gap.
**Keywords:** edge AI, Gemma 4, on-device AI, NVIDIA Jetson, DeepStream, backend architecture
**Status:** Not started.

### T8. Platform Engineering Ate DevOps. I Built the Internal Platform. Here's What Nobody Tells You.
Gartner: 80% of software orgs will have platform teams by end of 2026. "Is it just rebranding?" debate is active. Write first-person account of building internal developer platform, not another framework comparison.

**Why it works:** Tons of comparison articles, zero first-person build stories. You've built cloud-native platforms at scale.
**Keywords:** platform engineering, DevOps, internal developer platform, developer experience
**Status:** Not started.

### T9. After 14 Years of Coding, AI Made Me Love Programming Again (But Not How You Think)
Senior engineer burnout is acute: 66% report burnout symptoms. 34% feel no advancement path. Meanwhile AI changed the nature of the work. Write the nuanced "AI changed my relationship with the craft" story. How AI tools shifted you from tedious tasks back to interesting problems. Not toxic positivity, not despair.

**Why it works:** Burnout + AI intersection. All posts are either pure doom or pure hype. Nuanced senior perspective is rare.
**Keywords:** software engineer burnout, AI coding, senior developer, career, programming joy
**Status:** Not started.

### T10. I Built a Custom RTSP-to-WebRTC Proxy by Compiling Chrome. In 2026, AI Could Do It in a Weekend.
Existing RTSP/WebRTC draft + AI-assisted rebuild angle. "I built this from scratch when every SaaS failed, here's the war story. Then I asked Claude Code to rebuild it. Here's what happened." Combines deep domain expertise with timely AI angle.

**Why it works:** Niche but loyal audience (video infra engineers share aggressively). AI rebuild angle ties it to biggest trend. NAB 2026 just happened.
**Keywords:** RTSP, WebRTC, video streaming, libwebrtc, Chromium, AI coding, video proxy
**Status:** Not started.

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
