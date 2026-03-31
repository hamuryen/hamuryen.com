# How We Rescued a Critical Government Project in One Week

*A story about memory leaks, C#/C++ interop gone wrong, and inheriting a codebase with zero documentation.*

---

I joined a project that was already on fire.

The previous engineering team had left. No handover, no documentation, no knowledge transfer. What we inherited was a multi-server system that crashed every 5-6 hours. 16GB of RAM on each server, filling up until the OS killed the process. A government client who had been dealing with this for months.

The servers were being manually restarted multiple times a day. That was the normal operating procedure.

We had to figure out why and fix it.

## The Setup

The system was a distributed platform written in C# running on IIS across 4 servers, each with 16GB of RAM. Somewhere between 50 and 100 client applications connected to these servers using ZeroMQ for real-time messaging.

ZeroMQ doesn't have a native C# implementation. The previous team had written a C++ native library for ZeroMQ and wrapped it with a C++/CLI interop layer. A managed wrapper around unmanaged memory. If you've worked with native interop in .NET, you know this is exactly the kind of boundary where things break silently.

And that's exactly what happened.

## Finding the Leak

No documentation, no one to ask. We had to reverse-engineer the system from the running code. I started with the basics: observe, measure, hypothesize, verify.

**Observation.** I watched the memory on each server. Steady, relentless climb. No sudden spikes, just a slow bleed. This meant it wasn't one big allocation going wrong. Something small was happening thousands of times without ever getting cleaned up.

**Instrumentation.** I added logging around the ZeroMQ wrapper layer, right at the boundary between managed C# and unmanaged C++. I wanted to see every socket creation, every message operation, and every cleanup call.

**The discovery.** The logs showed that the C++ destructor (`~Class`) for the ZeroMQ wrapper objects was being called. But the actual native resource cleanup (`zmq_close()` and friends) never happened.

I dug into the wrapper code and found the problem.

## The Root Cause

The C++/CLI wrapper had a destructor (`~Class`) which maps to `IDisposable.Dispose()` in .NET. But it was missing the finalizer (`!Class`), the safety net that the garbage collector calls when nobody explicitly calls `Dispose()`.

Without `!Class`, if the C# code didn't call `Dispose()` on every single wrapper object (and it didn't, not consistently), the native handles just leaked. Sockets, contexts, message buffers, all allocated in unmanaged memory, invisible to the .NET garbage collector, never freed.

Every client connection, every message exchange leaked a small amount of unmanaged memory. With 50-100 clients connected and thousands of messages per minute through ZeroMQ, those small leaks added up. 16GB in 5-6 hours.

The GC had no idea. From .NET's perspective, everything was fine. From the OS perspective, the process was eating memory until it choked.

## The Fix

Once we understood the problem, the fix itself was straightforward:

1. **Added the missing `!Class` finalizer** to the C++/CLI wrapper so the GC could clean up native ZeroMQ handles even when `Dispose()` wasn't called
2. **Fixed deterministic cleanup** so `~Class` (Dispose) was being called explicitly in all code paths, not just some of them
3. **Added monitoring** for memory usage, connection tracking, and alerts for abnormal growth

Within a week the servers were stable. Memory stayed flat. The daily restarts stopped.

The client could finally use their system without interruption.

## What Came After

Fixing the memory leak put out the fire. But the underlying architecture had deeper problems. Tightly coupled monolith, no clear service boundaries, no REST APIs, a rigid permission model that made it hard to extend.

Over the next year we redesigned the entire platform from scratch:

- Decomposed the monolith into 60+ microservices
- Replaced ZeroMQ P2P with REST APIs for cleaner, more maintainable communication
- Introduced Docker and Kubernetes for deployment and orchestration
- Built a flexible permission system the client had been requesting for years
- Improved performance significantly across the board

The project went from near-cancellation to a success story. The client extended their contract and the platform served reliably for years.

## What I Took Away From This

**The interop boundary is always suspect.** When managed and unmanaged code meet, memory ownership gets ambiguous. In C++/CLI, `~Class` gives you `Dispose()` and `!Class` gives you the finalizer. You need both. Missing either one means either explicit cleanup doesn't work or the GC safety net doesn't exist.

**No documentation means no shortcuts.** We couldn't ask anyone what the code was supposed to do. We read it, instrumented it, and built our understanding from scratch. Slow, but thorough. Sometimes thorough is exactly what a failing system needs.

**Fix the bleeding first, then operate.** The temptation was to rewrite everything immediately. But the client needed stability now, not a perfect architecture in six months. We patched the leak in a week, kept the system running on that patched version for months, and used that time to properly design the replacement. Rushing a rewrite would have been a different kind of disaster.

**Small leaks sink big ships.** The leak wasn't dramatic. A few kilobytes per operation, thousands of times per hour. In long-running systems, even tiny resource leaks become critical. Monitor everything.

---

This was one of the defining projects of my career. Sometimes the most impactful engineering isn't building something new. It's saving something that's about to die.

**Want the technical deep-dive?** I wrote a detailed post about the exact C++/CLI pattern that caused this, with code examples and a checklist: **[The C++/CLI Destructor Trap: Why Your Native Wrapper Is Leaking Memory](https://post.hamuryen.com/)**

---

**About me:** I'm Burak Hamuryen, a Senior Software Engineer based in Berlin with 14+ years of experience in distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).
