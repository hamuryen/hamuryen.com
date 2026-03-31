# The C++/CLI Destructor Trap: Why Your Native Wrapper Is Leaking Memory

*If you're wrapping native C++ libraries in .NET using C++/CLI, there's a subtle mistake that can bring your production servers down. I found this out on a live government system that was crashing every 6 hours.*

---

## The Pattern That Looks Correct (But Isn't)

If you've written a C++/CLI wrapper around a native library, you've probably written something like this:

```cpp
// ManagedWrapper.h
public ref class ManagedWrapper
{
private:
    NativeResource* m_native;

public:
    ManagedWrapper()
    {
        m_native = new NativeResource();
    }

    // Destructor (~Class) maps to IDisposable.Dispose() in C#
    ~ManagedWrapper()
    {
        delete m_native;
        m_native = nullptr;
    }
};
```

Looks fine. The destructor is there. It cleans up the native resource. Ship it.

**This code has a critical flaw that will leak memory in production.**

## What's Missing: The Finalizer

C++/CLI has two cleanup mechanisms that serve different purposes:

**`~Class()` (Destructor)** — maps to `IDisposable.Dispose()`. Called explicitly by your code when you call `Dispose()` or use `using` blocks.

**`!Class()` (Finalizer)** — maps to `Object.Finalize()`. Called by the Garbage Collector when it collects the object and `Dispose()` was never called.

If you only have `~Class()` but not `!Class()`, your native resources will only be freed when someone explicitly calls `Dispose()`. If they forget (and in a large codebase, someone will forget), the .NET garbage collector will collect the managed wrapper object just fine, but the native memory it points to will never be freed.

The GC doesn't know about your `new NativeResource()`. It can't see unmanaged memory. Without `!Class()`, it has no way to clean it up.

## The Correct Pattern

```cpp
public ref class ManagedWrapper
{
private:
    NativeResource* m_native;

    void CleanUp()
    {
        if (m_native != nullptr)
        {
            delete m_native;
            m_native = nullptr;
        }
    }

public:
    ManagedWrapper()
    {
        m_native = new NativeResource();
    }

    // Destructor: IDisposable.Dispose()
    // Called explicitly by user code
    ~ManagedWrapper()
    {
        CleanUp();
        GC::SuppressFinalize(this);
    }

    // Finalizer: Object.Finalize()
    // Called by GC as safety net
    !ManagedWrapper()
    {
        CleanUp();
    }
};
```

Both `~Class` and `!Class` call the same `CleanUp()` method. The destructor also calls `GC::SuppressFinalize()` so the finalizer doesn't run unnecessarily if the user already disposed properly.

## Why This Matters

"My code always calls Dispose!" you say. Here are four scenarios where that breaks down:

### 1. Exception paths skip cleanup

```csharp
var wrapper = new ManagedWrapper();
DoSomethingThatThrows(); // Exception here
wrapper.Dispose();       // Never reached
```

Without `!Class`, this wrapper's native memory is gone forever. With `!Class`, the GC will eventually clean it up.

### 2. Collections silently replace objects

```csharp
var cache = new Dictionary<string, ManagedWrapper>();
cache["key1"] = new ManagedWrapper();
// ...later...
cache["key1"] = new ManagedWrapper(); // Old wrapper? Never disposed.
```

The old wrapper is silently replaced. Nobody calls `Dispose()` on it. Without `!Class`, that's a permanent leak.

### 3. Event handlers keep objects alive, then drop them

Objects subscribed to events can stay alive longer than expected. When they're finally released, if nobody calls `Dispose()`, only `!Class` can save you.

### 4. It compounds at scale

A few kilobytes per leaked object doesn't sound bad. But with 100 clients sending messages every second through your wrapper, that's thousands of leaked objects per minute. In our case, 16GB of RAM was gone in 5-6 hours.

## What This Looked Like in Production

I ran into this exact bug on a live government system. Four servers, each with 16GB of RAM, crashing every 5-6 hours. The cause: a C++/CLI wrapper around ZeroMQ that had `~Class` but not `!Class`.

The servers were being manually restarted multiple times a day. This had been going on for months before we got involved.

Adding `!Class` and fixing the disposal patterns across the codebase stabilized the system within a week. I wrote the full story here: [How We Rescued a Critical Government Project in One Week](https://post.hamuryen.com/how-we-rescued-a-critical-government-project-in-one-week-d6a8078354c7).

## Checklist

Before you ship any C++/CLI wrapper to production:

- [ ] `~Class()` exists for explicit deterministic cleanup (IDisposable)
- [ ] `!Class()` exists as a GC safety net for unmanaged resources
- [ ] Both call the same cleanup logic
- [ ] `~Class()` calls `GC::SuppressFinalize(this)`
- [ ] Cleanup checks for nullptr before deleting
- [ ] C# consumers use `using` blocks or explicitly call `Dispose()`
- [ ] You have memory monitoring in place

## The Pure C# Equivalent

If you're wrapping native resources in pure C# via P/Invoke or `SafeHandle`, the same principle applies:

```csharp
public class NativeWrapper : IDisposable
{
    private IntPtr _handle;
    private bool _disposed = false;

    public NativeWrapper()
    {
        _handle = NativeMethods.CreateResource();
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    ~NativeWrapper()
    {
        Dispose(false);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (_handle != IntPtr.Zero)
            {
                NativeMethods.DestroyResource(_handle);
                _handle = IntPtr.Zero;
            }
            _disposed = true;
        }
    }
}
```

Same idea: always implement both `Dispose()` and the finalizer when you own unmanaged resources.

## TL;DR

| If you only have... | What happens |
|---------------------|-------------|
| `~Class` only | Native memory leaks when Dispose() isn't called explicitly |
| `!Class` only | No deterministic cleanup, GC cleans up eventually but unpredictably |
| Both `~Class` and `!Class` | Correct: explicit cleanup when possible, GC safety net when not |

The missing `!Class` is a silent killer. Your app will work fine in development, pass all tests, run perfectly for a few hours. Then it will slowly consume all available memory and crash.

Don't ship a C++/CLI wrapper without the finalizer. I've seen what happens when you do.

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience. I've worked on systems handling 10K+ Kubernetes pods, 5,000+ camera streams, and $100M+ daily transactions. More at [hamuryen.com](https://hamuryen.com).*
