# GitHub Will Train AI on Your Copilot Data by April 24. Here's How to Stop It.

*A 30-day opt-out window. A policy change that affects every developer using Copilot Free, Pro, or Pro+. And 232 downvotes on GitHub's own discussion thread.*

---

I found out about this the way most developers did: someone posted it on Hacker News. On March 25, 2026, GitHub quietly updated its Privacy Statement and Terms of Service. Starting April 24, Copilot interaction data from Free, Pro, and Pro+ users will be used to train AI models by default. If you don't opt out before that date, your data is in.

This isn't about your private repository source code sitting on GitHub's servers. GitHub is clear about that: code "at rest" in private repos is not used for training. What changes is everything that flows through Copilot while you work: prompts, code snippets, suggestions you accept or modify, file names, repository structure, comments, and the context around your cursor position.

If you use Copilot on a private codebase, pieces of that code are now training data.

## What Exactly Gets Collected

[GitHub's FAQ](https://github.com/orgs/community/discussions/188488) breaks it down:

- **Inputs**: prompts and code context sent to Copilot (the code around your cursor, your comments, your questions in chat)
- **Outputs**: suggestions Copilot generates and whether you accepted, modified, or rejected them
- **Code snippets**: the actual code fragments that flow between you and Copilot during a session
- **Metadata**: file names, repository structure, navigation patterns, feature interactions, thumbs up/down feedback

This is collected while you're actively using Copilot. When you're working in a private repository and Copilot reads the surrounding code to generate a suggestion, that surrounding code becomes an "input" that can be used for training.

## Who Is Affected (and Who Isn't)

**Affected:**
- Copilot Free users
- Copilot Pro users ($10/month)
- Copilot Pro+ users ($39/month)

**Not affected:**
- Copilot Business users
- Copilot Enterprise users

These plans are governed by separate Data Protection Agreements that explicitly exclude training.

If you're paying $39/month for Pro+ and assumed your data was protected the same way enterprise customers' data is, it's not. Enterprise gets a contractual guarantee. You get an opt-out toggle.

## How to Opt Out of GitHub Copilot AI Training

Takes 30 seconds:

1. Go to [github.com/settings/copilot](https://github.com/settings/copilot)
2. Under **Privacy**, find "Allow GitHub to use my data for AI model training"
3. Set it to **Disabled**

That's it. If you previously opted out of data collection for product improvements, your preference is preserved. You don't need to do anything.

**The catch:** opting out only stops collection going forward. GitHub hasn't said whether data collected before you opt out will be removed from training sets. Once a model is trained on data, you can't untrain it.

## Why Developers Are Angry

[The GitHub community discussion](https://github.com/orgs/community/discussions/188488) has 232 downvotes. Out of 39 community posts, only one (from a GitHub VP) supported the change.

The frustration comes down to three things:

**1. Opt-out instead of opt-in.** The default is that your data gets collected. You have to actively go turn it off. For a platform that hosts private repositories containing proprietary business logic, trade secrets, and security-sensitive code, defaulting to "we use your data" is a choice. GDPR in Europe typically requires opt-in for new data processing purposes, not opt-out. GitHub claims "legitimate interest" as their legal basis for EEA/UK users, but legal experts have questioned whether that holds up for AI model training.

**2. The Pro+ gap.** Copilot Pro+ costs $39/month but doesn't include the same data protection that Business/Enterprise gets. You're paying premium pricing with free-tier privacy. The only way to guarantee your code isn't used for training is to upgrade to a Business plan with a Data Protection Agreement. For individual developers and small teams, that's not always an option.

**3. The "interaction data" framing.** GitHub is careful to say they're collecting "interaction data," not "your code." But interaction data includes code snippets, prompts containing code, and the code context around your cursor. When you're working on a private repository, there's no meaningful distinction between "interaction data" and "your private code." The code flows through Copilot, and now it flows into training data.

## The GDPR Question

GitHub's updated privacy statement specifies "legitimate interest" as the lawful basis for processing EEA/UK users' data for AI development. This is one of six legal bases under GDPR, and it's the most contested one for AI training.

The core issue: GDPR's legitimate interest requires a balancing test. The organization's interest in processing the data must not override the data subject's rights and freedoms. For code that's explicitly stored in private repositories because the owner wants it private, the argument that training AI models is a legitimate interest that overrides the owner's privacy expectation is thin.

The EU AI Act adds another layer. It includes provisions on training data transparency that may require GitHub to provide more granular controls over what data goes into which models.

No legal challenge has been filed yet, but the conditions are there. A European developer or company whose proprietary code was used for Copilot training without explicit consent would have a reasonable case under GDPR Article 6.

I'm based in Berlin. Every private repository I work on contains code owned by EU-based entities. The idea that this code could flow into AI training under an opt-out model, when GDPR was designed to prevent exactly this kind of default data collection, is hard to square. I opted out immediately, but the fact that I had to opt out rather than opt in is the problem.

For companies with EU employees using Copilot Free or Pro, this is worth raising with your legal or compliance team. The policy change may not align with your existing data processing agreements, especially if developers are working on client code covered by NDAs or separate data protection terms.

## What I'm Doing

I've opted out. The setting change takes 30 seconds and there's no downside. Copilot works exactly the same way after opting out. You just stop contributing to the training pool.

Beyond that:

**Auditing what flows through Copilot.** I'm more conscious now about what context Copilot sees. If I'm working on security-sensitive code (auth, encryption, API keys in config), I consider whether I want that flowing through any external service, regardless of training policies.

**Evaluating alternatives for sensitive projects.** For proprietary work, tools like [Tabnine](https://www.tabnine.com/) (never stores or trains on your code, offers self-hosting) or [Continue](https://continue.dev/) (open-source, bring your own model) provide similar functionality without the data collection question.

This isn't the end of the world. But it does require 30 seconds of your time and a conscious decision about where your code goes.

## The Bigger Picture

This is part of a pattern. Every AI-adjacent company is looking for more training data. The public internet has been mostly scraped. Open-source repositories have been scraped. The next frontier is proprietary code that users actively share with AI tools during their work.

GitHub's move is the most visible because they host the largest collection of code in the world and because the transition from "we don't train on your data" to "we train on your data by default" is a clear shift. But the underlying dynamic applies to every AI coding tool: when you send code to a cloud service, you're trusting that service's data practices.

The opt-out is the minimum. The real question is whether you're comfortable with any external service processing your most sensitive code, and whether the productivity gains justify that trust.

Go to [github.com/settings/copilot](https://github.com/settings/copilot). Check your settings. Make a decision. You have until April 24.

---

## Further Reading

- [GitHub Changelog: Privacy Statement and ToS Updates](https://github.blog/changelog/2026-03-25-updates-to-our-privacy-statement-and-terms-of-service-how-we-use-your-data/)
- [GitHub Blog: Copilot Interaction Data Usage Policy](https://github.blog/news-insights/company-news/updates-to-github-copilot-interaction-data-usage-policy/)
- [GitHub Community FAQ (232 downvotes)](https://github.com/orgs/community/discussions/188488)
- [The Register: GitHub Will Train on Your Data](https://www.theregister.com/2026/03/26/github_ai_training_policy_changes/)
- [InfoQ: GitHub Will Use Copilot Data from Free/Pro/Pro+ Users](https://www.infoq.com/news/2026/04/github-copilot-training-data/)
- [dev.to: GitHub Copilot Is Training on Your Private Code Now](https://dev.to/alanwest/github-copilot-is-training-on-your-private-code-now-you-probably-didnt-notice-2f6)
- [HN Discussion: If You Don't Opt Out by April 24](https://news.ycombinator.com/item?id=47548243)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
