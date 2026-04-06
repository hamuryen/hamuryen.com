# What Actually Works When Coding with AI (And What Doesn't)

*Not 50 tips. Not a listicle. Just what I've learned from using AI coding tools daily for over a year, including the parts nobody talks about.*

---

I've been writing code with AI tools every day for a while now. Claude Code for backend and architecture. Cursor when I need to see things visually. Copilot for autocomplete in the background.

Some of it has genuinely changed how I work. Some of it is a waste of time that I had to learn the hard way. And a [2025 METR study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) found that experienced developers were actually 19% slower with AI, even though they believed they were 20% faster. That gap between perception and reality is worth paying attention to.

Here's what I actually do, what I stopped doing, and why.

## Plan Before You Code

Every developer who's genuinely productive with AI does the same thing. They don't start with "build me X." They plan first.

My workflow for anything non-trivial:

1. **Research**: Ask Claude to explore the codebase in Plan Mode (read-only). "Read the auth module and explain how sessions work." No code gets written here.
2. **Plan**: Ask for a written plan with file paths, approach, and trade-offs. I open it in my editor (Ctrl+G in Claude Code) and add inline notes directly into the document. "This part should use the existing UserService, not a new one." Then I send it back: "I added notes, address them, update the plan. Don't implement yet." Sometimes we go back and forth 3-4 times.
3. **Implement**: Switch to Normal Mode. "Implement the plan. Run tests after each step. Mark tasks as done in the plan."
4. **Commit**: Small, frequent commits after each logical chunk.

[Boris Tane](https://boristane.com/blog/how-i-use-claude-code/) has the most disciplined version of this I've seen. His annotation cycles go 1-6 rounds before a single line of code gets written. His philosophy: "I want implementation to be boring. The creative work happened in the annotation cycles."

[Addy Osmani](https://addyosmani.com/blog/ai-coding-workflow/) quotes Les Orchard calling it "waterfall in 15 minutes." Same idea, different phrasing.

The point is: if you let AI jump straight into coding, it often solves the wrong problem. Planning costs 5 minutes. Fixing the wrong solution costs an hour.

For small tasks (rename a variable, fix a typo, add a log line) skip the plan. Just ask directly. If you can describe the diff in one sentence, planning is overhead.

## Context Is Everything

Everything in a Claude Code session (your messages, files it reads, command outputs, CLAUDE.md, memory) goes into one context window. When it fills up, Claude starts forgetting things and making mistakes.

[Philipp Spiess](https://spiess.dev/blog/how-i-use-claude-code) describes Claude as "a new grad with amnesia." It needs explicit context every single time. And the longer your session runs, the worse the amnesia gets.

### What I do:

**`/clear` between tasks.** If I finished debugging an auth bug and now want to write a new API endpoint, I clear. Different task, clean context. His single most important tip: "If there's one thing I want you to take away from this, it's that you should absolutely call /clear more often."

**`/compact` at 60% capacity, not 95%.** Don't wait until Claude is already forgetting things. A 70K-token conversation compresses to about 4K tokens. Run it when you've finished a phase but aren't done with the task. `/compact Focus on the API changes we made`.

**Subagents for research.** When I need Claude to understand a part of the codebase, I tell it to use a subagent. The subagent reads files in its own context and reports back a summary. My main session stays clean.

```
Use a subagent to investigate how the payment module handles refunds.
Then tell me what you found.
```

**After two failed corrections, start over.** If Claude keeps getting it wrong after two attempts, the context is polluted with failed approaches. `/clear` and write a better prompt that includes what you learned. A clean session with a good prompt beats a long session with corrections.

### Name and resume sessions

```bash
claude -n payment-refactor
claude --resume payment-refactor
```

I work on 3-4 things across a week. Resuming by name instead of scrolling through unnamed sessions saves time.

### Slash commands worth knowing

Beyond `/clear` and `/compact`, a few others come up regularly:

**`/context`** shows a visual grid of how full your context window is. I check it before deciding whether to `/compact` or `/clear`.

**`/cost`** shows token usage for the session. Useful when you suspect a conversation is burning through tokens faster than expected.

**`/diff`** opens an interactive diff viewer for uncommitted changes. Faster than switching to a terminal for `git diff` when you want to review what Claude changed.

**`/plan`** enters Plan Mode directly from the prompt. I use this at the start of any non-trivial task instead of typing "plan this first, don't write code yet."

**`/rewind`** rolls back both the conversation and code changes to a previous point. When Claude goes down a wrong path, this is cleaner than manually undoing file changes. Think of it as conversation-level `git checkout`.

**`/init`** generates a starter CLAUDE.md for your project. Good starting point, though you'll want to trim it down.

**`/doctor`** diagnoses installation issues. If MCP servers aren't connecting or something feels off, run this first.

Type `/` in Claude Code to see the full list. Most of them you'll never need, but these save real time.

## Break Work Into Small Pieces

AI is bad at big things and good at small things. A prompt like "build me a user dashboard with filtering, pagination, and export" produces something that technically runs but has no consistency.

A [Hacker News commenter](https://news.ycombinator.com/item?id=44362244) put it well: "Break down your task into smaller chunks, 30 minutes worth of human coding max."

What works:

```
1. Create the UserDashboard component with a basic table layout.
   Follow the pattern in AdminDashboard.tsx.

2. Add column sorting. Click header to sort asc/desc.

3. Add a search filter above the table. Debounce 300ms.

4. Add pagination. 20 rows per page. Use the existing Pagination component.
```

Each step is one prompt, one commit. If step 3 goes wrong, I revert just that step.

**Reference existing patterns.** "Look at how AdminDashboard.tsx implements the table and follow the same approach" is 10x more effective than describing what you want from scratch.

**Be uncomfortably explicit about constraints.** "Don't add comments unless the logic is non-obvious. Don't add extra type annotations beyond what's needed. Don't add libraries we're not already using. Prefer simplicity and readability over cleverness." This prevents Claude from over-engineering, which is its default mode.

## Tests First, Then Code

This came up in almost every source I read. The consensus is strong: ask AI to write tests first, then the implementation.

One [highly upvoted HN comment](https://news.ycombinator.com/item?id=44362244): "The number one important thing: ask it to write tests first, then the code. And instruct it to not overmock or change code to make tests succeed."

Why it works: tests constrain the solution space. Without tests, Claude can generate anything that looks right. With tests, it has to generate something that passes specific checks. The tests become automated verification that runs during implementation, not after.

Bad:
```
Write a function that validates email addresses.
```

Better:
```
Write tests for an email validation function.
Test cases: user@example.com returns true,
"invalid" returns false, user@.com returns false.
Then implement the function. Run the tests. Fix any failures.
```

Without tests, Claude "blithely assumes everything is fine when things are broken."

## When AI Fails

AI coding tools fail in predictable ways. Knowing the patterns saves debugging time:

**Assumption propagation.** Claude misunderstands an early requirement and builds everything on top of it. The mistake stays hidden across multiple files until the architecture is set. The planning step catches this before code is written.

**Abstraction bloat.** 1,000 lines where 100 would do. Elaborate class hierarchies instead of simple functions. One [HN user](https://news.ycombinator.com/item?id=47494890) noted: "LLMs have a bad habit of being very verbose and rewriting things that don't need to be touched, so the surface area for change is much larger."

Fix: "Keep it simple. No classes unless absolutely necessary." Or after implementation: "Simplify this. It's over-engineered."

**The "5 minutes more" trap.** [Osmani describes it](https://addyo.substack.com/p/the-80-problem-in-agentic-coding): "The agent implements an amazing feature and got maybe 10% wrong, and you're like 'I can fix this in 5 more minutes.' And that was 5 hours ago." I've been there.

**Security gaps.** Missing input sanitization, missing authorization checks. One analysis found AI-co-authored PRs had up to 2.74x more security vulnerabilities. I don't trust AI with auth flows, permission checks, or input validation. Those get manual review.

**Completion lies.** Spiess observed: "Claude often incorrectly claims completion despite remaining issues." Always verify. Run the tests. Check the output. Don't take Claude's word for it.

## The 80% Problem

The [METR study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) tested 16 experienced developers on repos with 22K+ stars and 1M+ lines of code. 246 issues, averaging 2 hours each. AI made them 19% slower.

The weird part: after experiencing the slowdown, developers still believed AI had sped them up by 20%.

Why the perception gap? AI reduces cognitive load. Work feels easier even when it's not faster. You're less mentally tired at the end of the day, but the clock says you spent more time.

[Osmani's data](https://addyo.substack.com/p/the-80-problem-in-agentic-coding) from a broader survey: only 16% of developers experienced "great" productivity improvements. Top frustrations: "AI solutions that are almost right" (66%) and "debugging AI code takes longer than writing it myself" (45%).

This doesn't mean AI is useless. It means knowing where it helps and where it doesn't:

**Where AI saves me the most time:** boilerplate, test generation, exploring unfamiliar codebases, database queries, configs, repetitive patterns, code review prep.

**Where AI costs me time:** complex state management, security-sensitive code, anything with implicit business rules not captured in the codebase, large established codebases with unwritten conventions.

## Code Review: Don't Rubber-Stamp

Only 48% of developers consistently review AI-generated code before committing. The rest rubber-stamp it. I've done it too. Claude generates something, it looks right, tests pass, ship it. Three days later I can't explain how it works.

What I do now:

**Never review code you just watched being written.** You're biased. For important changes, I open a fresh session and ask Claude to review its own code with clean context. A second pair of "eyes" without the context of the first session catches things.

**Read the diff, not the file.** What changed? Why? Does the change match what I asked for?

**Commit frequently.** Small commits are your audit trail. If something breaks next week, `git bisect` finds which AI-generated change caused it.

## The Honest Downsides

I'd be lying if I said it's all upside. Some things bother me:

**The babysitting problem.** [Osmani's quote](https://addyo.substack.com/p/the-80-problem-in-agentic-coding) resonates: "I spend most of my time babysitting agents. You're not coding anymore, you're supervising. Watching. Redirecting. It's a different kind of exhausting."

**The joy question.** [Alexandru Nedelcu](https://alexn.org/blog/2025/10/27/ai-sucks-the-joy-out-of-programming/) (28-year career) wrote that AI gives you "all the bad parts about programming, like the stress generated by not being in control when things aren't working" without "any of the gratification, which comes from the journey itself." I don't fully agree, but I understand the feeling on frustrating days.

**Skill atrophy.** If you stop writing code manually, you get worse at it. The [METR study participants](https://domenic.me/metr-ai-productivity/) admitted AI made tasks "more fun" (it turned coding into a management game) but not actually faster. There's a risk of losing the underlying skill.

**The metrics trap.** A HN commenter on a popular productivity post: "Treating throughput of code going to production as a success metric, without any mention of quality, bugs, or maintenance burden is exactly the kind of thinking developers used to push back on." More PRs doesn't mean better software.

## What I Stopped Doing

**Asking for entire features at once.** Always produces inconsistent code.

**Long sessions without clearing.** Quality degrades. I `/clear` aggressively now.

**Trusting AI with security.** Auth, permissions, input validation get manual review every time.

**Skipping the plan.** Even 2 minutes of planning prevents 30 minutes of fixing.

**Writing massive CLAUDE.md files.** [Boris Cherny](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/), the creator of Claude Code, keeps his at about 100 lines. Most people write 500+. Shorter is better. Claude ignores rules buried in long files.

**Treating AI as a faster typewriter.** It's not. It's a different way of working. The developers who benefit most are the ones who reconceptualized their role: less typing, more directing, more reviewing, more planning.

---

## Further Reading

**Workflows:**
- [Addy Osmani: My LLM Coding Workflow Going Into 2026](https://addyosmani.com/blog/ai-coding-workflow/)
- [Boris Tane: How I Use Claude Code](https://boristane.com/blog/how-i-use-claude-code/)
- [Philipp Spiess: How I Use Claude Code](https://spiess.dev/blog/how-i-use-claude-code)
- [Neil Kakkar: How I'm Productive with Claude Code](https://neilkakkar.com/productive-with-claude-code.html)
- [Claude Code Official Best Practices](https://code.claude.com/docs/en/best-practices)

**Research:**
- [METR 2025: Measuring AI Impact on Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- [Addy Osmani: The 80% Problem in Agentic Coding](https://addyo.substack.com/p/the-80-problem-in-agentic-coding)
- [Domenic Denicola: Reflections on the METR Study](https://domenic.me/metr-ai-productivity/)

**Practical:**
- [Builder.io: 50 Claude Code Tips and Best Practices](https://www.builder.io/blog/claude-code-tips-best-practices)
- [Graphite: Programming with AI Workflows](https://graphite.com/guides/programming-with-ai-workflows-claude-copilot-cursor)
- [Ask HN: How Do You Actually Use Claude Code Effectively?](https://news.ycombinator.com/item?id=44362244)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
