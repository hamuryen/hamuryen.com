# You Probably Don't Need Microservices

*42% of organizations that adopted microservices are now consolidating back. Here's why, and how to know if you're one of them.*

---

I watched a 3-person team spend months setting up Kubernetes, Kafka, and a service mesh for an app that could have been a single Spring Boot jar. They were solving infrastructure problems instead of building their product. By the time the architecture was "ready," they'd burned through half their runway. The product never launched.

I've managed 60 microservices in production for a government platform. Kubernetes, ZeroMQ, Kafka, Docker, the whole stack. It was the right call for that project. But that project had multiple teams, independent deployment requirements, and government-scale traffic. Most projects don't.

The microservices hype peaked around 2018. Every conference talk, every job listing, every architecture review said the same thing: break it up, make it small, deploy independently. Netflix does it. Uber does it. You should too.

Except Netflix has thousands of engineers. You probably have twelve.

## The Numbers Nobody Mentions

A [2025 CNCF survey](https://www.cncf.io/reports/cncf-annual-survey-2024/) of 689 organizations found that **42% of companies that adopted microservices have consolidated at least some services back into larger units**. The primary reasons: debugging complexity, operational overhead, and network latency.

[Segment](https://www.infoq.com/news/2018/07/segment-microservices/) went from 140 microservices back to a monolith. Their engineer described it as "falling from the microservices tree, hitting every branch on the way down." After consolidating, they made 46 improvements to shared libraries in 6 months, compared to 32 in all of the previous year under microservices. They were moving faster with less architecture.

[Amazon Prime Video](https://www.primevideotech.com/video-streaming/scaling-up-the-prime-video-audio-video-monitoring-service-and-reducing-costs-by-90) moved their video monitoring tool from serverless microservices to a monolith and cut costs by 90%. The distributed architecture created excessive inter-service communication overhead and their Step Functions bill exploded.

Even [Istio](https://istio.io/latest/blog/2020/istiod/), the service mesh tool built specifically to manage microservices complexity, was itself rebuilt from microservices (Pilot, Citadel, Galley, sidecar injector) into a single binary called `istiod` in version 1.5. Their own blog post calls it "effectively the reversal of the microservice architecture model." The tool for managing microservices couldn't handle being microservices.

## What You're Actually Signing Up For

When someone says "let's use microservices," here's what they're really proposing:

**Network calls instead of function calls.** An in-process function call takes nanoseconds. A network call between services takes 1-10ms on a good day, 50-100ms under load. Multiply that by the number of services in your call chain. A request that touches 6 services accumulates at least 30ms of pure network overhead before any processing happens. In our government auction platform, we hit this wall during live bidding. A bid submission that touched the bidding engine, the user service, the payment validation service, and the notification service had to be carefully optimized to stay under acceptable latency. We made it work, but it took months of tuning that wouldn't have existed with a monolith. [Jeff Dean's research at Google](https://research.google/pubs/the-tail-at-scale/) showed that at the 99th percentile, a request touching 100 services where each has 99% availability still produces unacceptable tail latency.

**Distributed debugging.** In a monolith, you get a stack trace. In microservices, you get logs scattered across a dozen services, each with its own timestamp format and verbosity level. I've spent entire days tracing a single bug across services, correlating timestamps, reading logs from 4 different systems, only to find the root cause was a serialization mismatch between two services that nobody noticed because they were deployed independently. In a monolith, that's a compile error. You need correlation IDs, structured logging, and a tracing infrastructure (Jaeger, Zipkin, OpenTelemetry) just to reconstruct what happened. [Charity Majors](https://charity.wtf/) (CTO of Honeycomb, former Facebook infra) has argued that traditional logging is nearly useless in distributed systems and that most teams drastically underestimate the observability investment required.

**Your database stops protecting you.** This is the one that hurts the most in practice. In a monolith with a single database, you get foreign keys, cascade deletes, JOIN queries, and ACID transactions for free. The database enforces data integrity for you. Delete a user? CASCADE handles their orders, sessions, preferences. Query orders with customer names? One JOIN.

With microservices and database-per-service (which is the whole point, otherwise you have a distributed monolith), all of that disappears. No foreign keys across service boundaries. No cascade deletes. No JOINs. You delete a user in the user service, but their orders still exist in the order service pointing to a user ID that no longer exists. Now you need event-driven cleanup: user-deleted event, every service listens, each one handles its own cleanup logic. Multiply that by every entity relationship in your system.

Need data from two services? You can't JOIN. You make two API calls, get two payloads, and assemble them in application code. Pagination across services? Good luck.

And forget ACID transactions. "User places an order, payment is charged, inventory is decremented" is one database transaction in a monolith. In microservices, it's a saga: 3 services, 3 forward operations, 3 compensating rollbacks, all coordinated through events or an orchestrator. [Chris Richardson](https://microservices.io/patterns/data/saga.html) documents that sagas become unmanageable beyond 4-5 services. What happens when the payment succeeds but inventory update fails? You write a compensating transaction to refund. What if the refund fails? You write a retry. What if the retry fails? Welcome to distributed systems.

**Infrastructure per service.** Each microservice needs its own CI/CD pipeline, health checks, monitoring, alerting, log aggregation, secret management, and possibly its own database. Multiply by the number of services. A monolith might need 1-2 ops-focused engineers. An equivalent microservices setup typically requires 2-4 platform engineers plus operational burden distributed across product teams. Without a mature internal developer platform, developers end up spending a significant chunk of their time on infrastructure rather than features. This is why Spotify, Uber, and Netflix all invested heavily in dedicated platform teams before their microservices architectures became productive.

**Testing becomes a different job.** In a monolith, you write unit tests and integration tests that run against one codebase. In microservices, you need contract tests between every pair of services that communicate, integration tests that spin up multiple services, end-to-end tests that traverse the full call chain, and chaos engineering to verify failure modes. Contract testing alone (using tools like Pact) requires both the consumer and producer to maintain test contracts, and when they drift, you find out in production. A monolith doesn't need contract tests because everything compiles together.

**Nobody understands the whole system.** When you have 20+ services with their own codebases, deployment schedules, and data stores, no single person can hold the full picture in their head. [DHH calls this](https://world.hey.com/dhh/how-to-recover-from-microservices-ce3803cc) "murder for conceptual comprehension." Uber grew to 2,200 microservices and eventually had to reorganize them into [70 domains](https://www.uber.com/us/en/blog/microservice-architecture/) just to make the system comprehensible again. They didn't go back to a monolith, but they essentially admitted they went too far.

## The People Who Built This Stuff Are Telling You Not To

These aren't random Twitter takes. These are the people who literally wrote the books and built the tools.

**Sam Newman**, author of "Building Microservices" (the canonical O'Reilly book on the topic):

> "The monolith is not the enemy. Microservices should not be the default choice. Microservices are not a good choice for most startups."

The guy who wrote THE book on microservices says don't start with them.

**Martin Fowler**, who coined "MonolithFirst" in 2015:

> "Almost all the successful microservice stories have started with a monolith that got too big and was broken up. Almost all the cases where a system was built as a microservice system from scratch, it has ended up in serious trouble."

**Kelsey Hightower**, Distinguished Engineer at Google Cloud and one of the most influential voices in the Kubernetes ecosystem:

> "Monoliths are the future because the problem people are trying to solve with microservices doesn't really line up with reality."

> "You went from writing bad code to building bad infrastructure that you deploy the bad code on top of."

**DHH**, creator of Ruby on Rails:

> "Replacing method calls with network calls makes everything harder, slower, and more brittle. It should be the absolute last resort."

He points out that GitHub and Shopify both run their main applications as monoliths with millions of lines of code and thousands of programmers.

## The Distributed Monolith: The Worst of Both Worlds

The most common failure mode. You split your app into 20 services, but they share a database. Or they can't be deployed independently because service A needs service B's changes first. Or every feature requires coordinated PRs across 4 repositories.

Congratulations, you now have the operational complexity of microservices with none of the benefits. You've replaced compile-time errors with runtime network failures. Sam Newman calls this the most common failure mode of microservices adoption.

Signs you have a distributed monolith:
- You deploy multiple services together, every time
- A change in one service requires changes in 3 others
- Services share a database
- You can't test one service without spinning up 5 others
- Your "independent" services call each other synchronously in long chains

If any of these are true, you didn't build microservices. You built a monolith with network latency.

## Shopify's Alternative: The Modular Monolith

Shopify runs one of the largest Ruby on Rails monoliths in the world. About 2.8 million lines of Ruby, 1000+ developers, processing 173 billion requests on Black Friday 2024 alone. They explicitly chose not to go microservices.

Instead, they built [Packwerk](https://github.com/Shopify/packwerk), an open-source tool that enforces module boundaries within the monolith at the code level. It detects and prevents cross-boundary references, giving you the encapsulation benefits of microservices without the network overhead.

Why they chose this:
1. Network overhead would be unacceptable for their latency requirements
2. They didn't want the operational complexity
3. Team independence through code-level boundaries was enough

A modular monolith gives you clear separation, independent development, and the ability to extract services later if you genuinely need to. It's the exit ramp without the upfront highway toll.

## When Microservices Actually Make Sense

I'm not saying microservices are always wrong. I ran 60 of them. Here's when they were worth it:

**Multiple independent teams.** We had several teams that needed to deploy without coordinating with each other. Conway's Law is real: your architecture should mirror your org structure. If you have 5 teams each owning a domain, separate services make sense.

**Genuinely different scaling requirements.** Our auction engine needed to handle thousands of concurrent bids per second. The document management module needed to serve PDFs occasionally. Scaling them together would have been wasteful. This is a real signal.

**Regulatory isolation.** Payment processing under banking regulations needed to be isolated from the rest of the system. Separate service, separate audit trail, separate security boundary.

**Different technology requirements.** If one component genuinely benefits from a different language or runtime. Our real-time bidding engine had different performance characteristics than our reporting module.

**You've already proven the boundaries.** Martin Fowler's key insight: build the monolith first, discover the real boundaries through experience, then extract services where the need is proven. "Even experienced architects working in familiar domains have great difficulty getting boundaries right at the beginning."

## The Resume-Driven Development Test

I've been guilty of this myself. Early in my career, I picked technologies because I wanted to learn them, not because the project needed them. It's a natural instinct. You see Kafka in every job listing, so you add Kafka to your side project that processes 10 events per minute. An academic paper actually [formalized this as "Resume-Driven Development"](https://arxiv.org/pdf/2101.12703): overemphasizing technology trends to fill gaps in an applicant's profile rather than to solve a real problem.

The honest test: would I still pick this architecture if it didn't go on my resume? If the answer is "probably not," that's worth pausing on.

Some patterns I've seen more than once:
- Breaking an app into 50 services maintained by 2 developers
- Deploying Kubernetes for a project with 500 users
- Adding Kafka when your data flow is request-response
- Implementing a service mesh for 4 services

None of these are wrong in the right context. But the right context is rarely a startup with 5 engineers and no product-market fit yet.

## What I'd Actually Recommend

**Start with a monolith.** Make it modular. Use clear boundaries: separate modules, defined interfaces, no reaching into another module's database tables. Enforce boundaries with tooling if your language supports it (Packwerk for Ruby, ArchUnit for Java, module boundaries in Go).

**Extract a service when you have a real reason.** Not "we might need to scale this independently someday," but "this component is currently a bottleneck and we need to scale it now." Not "this team might want to deploy independently," but "this team's deployment schedule is blocked by another team every sprint."

**If you're a small team, you almost certainly don't need microservices.** Basecamp serves 3.3 million users across 75,000 companies with about 37 engineers and a monolith. DHH built the original with 12 programmers. Shopify handles Black Friday with a monolith and 1000+ developers. You're not bigger than Shopify.

**If you already have microservices and it hurts, consolidate.** You're in good company. Amazon, Segment, Istio, and 42% of the CNCF survey respondents are doing the same thing. There's no shame in it. The shame is in paying the complexity tax when you don't have to.

The best architecture is the simplest one that solves your actual problems. Not your hypothetical future problems. Not Netflix's problems. Yours.

---

## Further Reading

**Case Studies:**
- [Amazon Prime Video: 90% Cost Reduction by Moving to Monolith](https://www.primevideotech.com/video-streaming/scaling-up-the-prime-video-audio-video-monitoring-service-and-reducing-costs-by-90)
- [Segment: Goodbye Microservices](https://www.infoq.com/news/2018/07/segment-microservices/)
- [Shopify: Deconstructing the Monolith](https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity)
- [Uber: Domain-Oriented Microservice Architecture](https://www.uber.com/us/en/blog/microservice-architecture/)

**Perspectives:**
- [Martin Fowler: MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html)
- [DHH: How to Recover from Microservices](https://world.hey.com/dhh/how-to-recover-from-microservices-ce3803cc)
- [Kelsey Hightower: Monoliths Are the Future](https://changelog.com/posts/monoliths-are-the-future)
- [Sam Newman: Monolith to Microservices](https://samnewman.io/books/monolith-to-microservices/)

**Data:**
- [CNCF Annual Survey 2024-2025](https://www.cncf.io/reports/cncf-annual-survey-2024/)
- [The Tail at Scale (Jeff Dean, Google)](https://research.google/pubs/the-tail-at-scale/)
- [Resume-Driven Development (Academic Paper)](https://arxiv.org/pdf/2101.12703)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
