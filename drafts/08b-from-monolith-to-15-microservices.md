# From Monolith to 15 Microservices: When It Actually Made Sense

*Everyone's writing about going back to monoliths. Here's why we went the other way in 2013, before "microservices" was even a word we knew.*

---

In May 2011, a group of software architects met at a workshop near Venice and started describing something they called "micro services." By May 2012, they settled on the name "microservices." [Martin Fowler and James Lewis published the article](https://martinfowler.com/articles/microservices.html) that made the term mainstream in March 2014.

I didn't read any of that. In late 2013, I was an engineer at a small defense and video analytics company going through a transition. Most of the senior engineers had left. I was mid-level with about a year of experience, but I was the most experienced developer on the team. I split a C++ application into 15 separate services because the monolithic version we'd built the year before was getting in the way.

Same idea. Different continent. No buzzwords.

## The Monolith We'd Already Built

The year before, we'd built a video management system for a client. C++, Qt for the desktop frontend, PostgreSQL for the database, gSOAP for the service layer. Standard stack for the era. It was a monolith: one codebase, one build, one deployment.

It worked fine for a single client. But when we decided to build our own product, a VMS we'd sell to multiple customers and deploy on-premise at their sites, the monolith's limits became obvious. Every change to the camera integration module required rebuilding and redeploying the entire system. Authentication code that hadn't changed in months got retested because it shared a binary with alerting code that changed weekly. Different features had completely different update cycles, but they were all locked together.

So for the new product, I designed it differently. Not because I'd read about microservices. Because I'd experienced the monolith, and I didn't want to do it again.

## Splitting It Up

I broke the system into about 10-15 separate services. Each one was its own C++ project, its own binary, its own process:

- **User service**: authentication, login, permissions, roles
- **Camera/asset service**: device management, stream configuration, brand-specific integrations
- **Recording service**: storage management, retention policies, playback
- **Live view service**: real-time stream distribution to clients
- **Alerting service**: rule engine, event triggers, notifications
- **Analytics service**: video analytics processing, detection events
- And several more for logging, configuration, licensing

Each service had its own PostgreSQL schema within a shared database instance. The user service owned the `users` schema, camera management owned `assets`, alerting owned `alerts`. They didn't reach into each other's tables. We couldn't afford to run 15 separate database instances for a product that would be deployed on whatever hardware the customer had on-premise, but the schema separation meant services stayed out of each other's data.

I built the architecture and the foundation. Then two developers joined: one junior, one with about a year of experience. Three people, 15 services.

## Why We Used SOAP Instead of REST in 2013

If you've only ever worked with REST and JSON, brace yourself.

In 2013, SOAP was still the enterprise standard. REST was gaining ground, especially in the web world, but in C++ desktop applications talking to backend services, SOAP with gSOAP was the established tool. REST frameworks for C++ were immature or nonexistent. gSOAP gave us code generation from WSDL definitions, type-safe communication, and a protocol that worked.

It also gave us headaches.

gSOAP generates C++ code from your service definitions. You define the interface, run the generator, and get a pile of .cpp and .h files with XML serialization for every data type. For a single service calling a single other service, it works fine. Clean, structured, predictable.

The problem starts when one service needs to call multiple other services. The alerting service needed to talk to both the user service (to check permissions) and the camera service (to get device info). That meant including generated code from both services in the same project. And that's where gSOAP broke down.

Namespace collisions. The generated code from the user service defined types and serialization functions that clashed with the generated code from the camera service. The solution was wrapping each client in its own C++ namespace, carefully isolating the generated files, and making sure nothing leaked across boundaries. It was tedious, fragile, and error-prone. Add a field to one service's API and you'd spend an afternoon fixing compile errors in a consuming service that didn't change at all. This was a [well-documented pain point](https://gsoap.yahoogroups.narkive.com/A1fju6wM/problem-with-c-namespaces-using-the-generated-files) in the gSOAP community.

And then there was the XML overhead. Every call serialized data to XML, sent it over the wire, and deserialized on the other side. For the kind of data we were passing (device lists, user permissions, alert configurations), the XML payload was often 5-10x larger than the actual data. Not a disaster on a local network, but wasteful.

If I were doing it today, I'd use REST with JSON, or gRPC for the performance-sensitive paths. In 2013, those weren't real options for C++. gSOAP was what we had, and it worked. Just not gracefully.

## No Docker, No Kubernetes, No Problem

Each service ran as a Linux service on CentOS. Start, stop, restart independently. Check logs in `/var/log/`. That's it.

No containers. Docker had just released version 0.9 in 2013 and nobody in our world had heard of it. Kubernetes didn't exist yet (Google released it in 2014). We didn't have service discovery, load balancing, or health checks. Services found each other through configuration files that listed IP addresses and ports.

Deployment meant updating one binary on the customer's server and restarting that one systemd service. When we needed to update the alerting service, we updated the alerting service. The camera service kept running. The user service kept running. No coordinated restart, no deployment pipeline, no downtime.

For on-premise deployments to customers who didn't have cloud infrastructure (cloud wasn't really an option for most of our customers in 2013), this simplicity was the whole point. The product ran on whatever server the customer had. Sometimes powerful, sometimes not. It had to be light.

## What We Got Wrong

**No centralized logging.** Each service logged to its own file. When a problem spanned multiple services, we'd open 4-5 terminal windows, tail different log files, and try to match timestamps by eye. A correlation ID flowing through all services would have saved us hours. We didn't implement one because we didn't know it was a pattern.

**No service discovery.** Hardcoded IPs and ports in config files. Fine for a few deployments, painful for dozens. Every new customer site meant manually editing configuration.

**gSOAP for everything.** We used it because we knew it, not because it was the best fit. The namespace collisions, the XML overhead, the code generation friction. A lighter protocol would have been better, but the C++ ecosystem in 2013 didn't offer many alternatives.

**No health checks or circuit breakers.** If the user service went down, the alerting service would keep trying to call it and eventually time out. No graceful degradation, no automatic recovery detection. We handled it with manual monitoring and restarts.

## Why It Worked Anyway

Three people, 15 services, SOAP over gSOAP, CentOS, no containers, no orchestration, manual on-premise deployments. Sounds like it shouldn't work. But it did, for years. Here's why:

**The boundaries were obvious.** Cameras are not users. Users are not alerts. Alerts are not recordings. We didn't need Domain-Driven Design workshops to figure this out. The previous monolithic project had already shown us where the natural seams were. We just made them explicit.

**The team was small enough.** Three people sitting next to each other. Communication overhead was zero. We didn't need API contract management or service catalogs. We talked across the desk.

**The number was right.** 10-15 services, not 60, not 200. Everyone could hold the full system in their head. Every person could debug every service. There was no "that's the other team's service" problem because there was no other team.

**On-premise forced simplicity.** No cloud auto-scaling, no managed databases, no infinite compute. The product had to run on real hardware at real customer sites. This constraint killed over-engineering before it started. If it couldn't run on a single server, it was too complex.

## What I Realized Later

When Docker and Kubernetes exploded in 2017-2018 and "microservice architecture" became the thing everyone was talking about, I realized we'd been doing it for years. Different tools, same principles: independent deployment, domain-based separation, separate data ownership, process isolation.

The 2018 version came with an ecosystem we didn't have: containerization, orchestration, distributed tracing, service meshes, circuit breakers. Tools that solve real problems. But tools that also add real complexity. We shipped a working product without any of them.

I've since worked on much larger systems with many more services, Kubernetes, Kafka, the full modern stack. The honest comparison: 15 well-bounded services with simple communication was easier to operate than larger architectures with sophisticated tooling. More services doesn't mean better architecture. It usually means more things that can break.

## When Splitting Actually Makes Sense

From doing this more than once:

**When you've already built the monolith.** We built the monolithic version first. It taught us where the real boundaries were. When we built the product, we already knew which modules belonged together and which didn't. Starting with microservices on day one is guessing. Starting after you've seen the domain is informed.

**When modules have different lifecycles.** Our camera integration changed every week as we added new brands. Authentication changed once a quarter. Forcing them into the same build and deployment cycle was the actual problem.

**When the domain boundaries are obvious.** If you have to argue about where to draw the line, maybe the line doesn't exist yet. Our boundaries were clear because cameras, users, alerts, and recordings are genuinely different things with different data and different logic.

**When you can keep the number small.** 10-15 services for 3 engineers worked. Each person understood every service. The moment you have services that nobody fully understands, you've gone too far.

If none of these apply to you, I wrote another post about why you probably don't need microservices at all. (Link coming when both posts are published.)

---

## Further Reading

- [Martin Fowler & James Lewis: Microservices (2014)](https://martinfowler.com/articles/microservices.html)
- [Martin Fowler: MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html)
- [gSOAP C++ Namespace Issues (Community Thread)](https://gsoap.yahoogroups.narkive.com/A1fju6wM/problem-with-c-namespaces-using-the-generated-files)
- [Sam Newman: Building Microservices (O'Reilly)](https://samnewman.io/books/building-microservices/)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
