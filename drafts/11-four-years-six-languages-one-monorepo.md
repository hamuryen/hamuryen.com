# 4 Years, 6 Languages, 1 Monorepo: What I'd Do Differently

*Shared code made integration easier. Keeping everyday work fast took more care.*

![Six distinct code stacks connected on one shared foundation](assets/four-years-six-languages-one-monorepo-cover.png)

*One place to change the system. Different parts to build, test, and release.*

Over roughly four years, I worked in a monorepo with six languages and around 20 to 30 services and components. There were backend services, plugins, web applications, and AI components. They shared a repository, but they did not all behave like the same kind of project.

The clearest benefit was integration.

When a model or DTO changed, it was easier to find the affected code and update it together. A DTO is the object used to carry data between parts of a system. Changing its shape can mean changing a producer, a consumer, tests, and sometimes a user interface.

Having those pieces in one place reduced the risk of overlooking an incompatible change. I could look at the whole change instead of reconstructing it across several repositories and pull requests.

I also remember waiting. Tests and hooks took time. Changes around base layers brought in tests far from the task I was working on. Commits arrived from unrelated parts of the repository. Keeping standards consistent needed attention, and changes to the release structure needed following.

Both sides belong in the story. I would want to keep the integration benefit. I would put more deliberate work into the daily cost of sharing the repository.

## Keep the cross-service change visible

Consider a small example: a backend adds a field to a response, a plugin reads it, and a web application displays it.

In one repository, the pull request can show the producer, the consumers, and the tests together. A reviewer can follow the field from its definition to its use. If code generation is involved, the schema and generated clients can be checked as part of the same change.

That does not prove the feature works. It does make some missing pieces easier to notice. The plugin may still expect the old field name. A test fixture may use the wrong type. The web application may assume a value is always present.

This is the part of a monorepo I would protect. Moving everything apart just to make each directory quieter can introduce another cost: coordinating changes that used to be visible in one diff.

That visibility should help reviewers too. A contract change should explain which components produce it, which consume it, and which versions may coexist. A large pull request containing all the code still needs a readable explanation of the dependency between its parts.

The repository gives you a convenient place to inspect integration. The review process has to use it.

## “Unrelated to my task” is not always “unaffected”

One frustrating part was seeing tests run in areas that seemed unrelated to the change I wanted to make.

There are two different problems hiding there.

A test may run because the pipeline selects too much work. It may also run because a shared base layer really does connect those areas. In the second case, skipping the test would hide the dependency without removing it.

Today, my first question would be why a target was selected. Which changed input led to this test? Was it a source dependency, a generated file, a compiler setting, or a global configuration change?

Pants documents the difference between checking changed files and including their dependents. Its CI guide uses transitive changed dependents for checks that need to account for downstream effects, and it calls out cases where configuration changes need broader validation. [1](https://www.pantsbuild.org/stable/docs/using-pants/using-pants-in-ci)

That is a useful principle even when the repository uses another build tool. Directory filters alone are a weak model of how software depends on other software.

In a repository with several build systems, the boundaries between their graphs need checking too. If a schema change feeds generated code in another language, that edge must exist somewhere the CI selection process understands. Each tool can be correct about its own targets while the overall pipeline still misses a consumer.

The goal would be a test selection I can explain and trust. On changes where the graph is incomplete or a shared toolchain changes, a broader run is reasonable.

## Give the base layer a smaller job

A shared layer is attractive because another service already needs something similar. Over time, it can become a convenient home for things that have little in common.

Logging helpers arrive beside domain models. A small utility gains a dependency on a large client library. More services import the package because they need one function from it.

Then a small edit reaches further than expected.

I would review heavily shared packages by asking what their consumers actually need. Can stable protocol definitions stand on their own? Can a small utility avoid pulling in application-specific code? Does a domain rule belong with its owning service instead of the lowest common layer?

I would not split every helper into a separate package. That has its own maintenance cost. I would start with dependencies that repeatedly widen builds and tests, or make an otherwise local change difficult to release.

This is where the waiting becomes useful evidence. A slow CI job may be a tooling problem. It may also be showing you that the code has become more connected than the team intended.

Renaming a directory will not change that. Narrowing a real dependency can.

## Put short feedback close to the edit

Long hooks were another recurring irritation. A commit is a small action in a developer's day. Attaching too much work to it makes the cost appear again and again.

If I were setting the policy today, I would give local checks a clear purpose: catch cheap, obvious mistakes quickly. Formatting, basic linting, and selected fast checks fit that purpose. A broad integration suite usually needs another place to run.

The pre-commit framework supports file filters and hook stages, so hooks do not all need to run on every file at the same point in the workflow. Its configuration also supports pinned hook revisions. [2](https://pre-commit.com/)

The harder decision is what to put behind those settings. I would ask developers to run a small relevant test target while editing, keep commit-time work predictable, and let required CI checks enforce the wider policy before merging.

Local hooks are useful feedback, but they can be bypassed or missing. They should not be the only place a required check exists.

Waiting for a runner deserves its own measurement. To a developer, queue time and execution time are both time lost. Adding a cache does not help much if most of the wait happens before the build begins.

The measurement I would keep is time from a change to actionable feedback, including slower cases. A collection of impressive individual job times can still produce an unpleasant working day.

## Cache results only when the inputs are understood

A shared build cache can remove repeated work across machines. In a repository this size, that is worth taking seriously.

It is also worth understanding what makes a result reusable.

Bazel's remote cache works with build actions and their declared inputs and outputs. Its documentation warns about tools outside the workspace that are not tracked as inputs. A cache cannot account for a relevant dependency that the build description leaves out. [3](https://bazel.build/remote/caching)

Compiler and tool versions, generator inputs, environment dependencies, and lockfiles all deserve checking before a high cache-hit rate counts as success. A fast result is only useful if it belongs to the current inputs.

Clean and warm builds need separate measurements, with attention to the jobs that determine the overall completion time. Saving work on many small targets may barely change the time a developer waits for one long, uncached integration job.

This would also make cache failures easier to discuss. “The cache did not help this change” is more useful when we know whether the cause was changed inputs, missing entries, download time, or a job that could never reuse a result in the first place.

## Make Git easier to read and cheaper to use

The repository had a steady flow of commits from parts of the system unrelated to my immediate work. Following that traffic made everyday Git work harder.

Some of that was an attention problem. The amount of data in a large repository raises a different set of questions.

For attention, path-limited history helps when investigating one area. For example, with illustrative directory names:

```sh
git log --oneline -- services/payments/ packages/contracts/
```

Git supports limiting history by paths. That gives me a more focused view; it does not create an independent branch history or remove dependencies outside those paths. [4](https://git-scm.com/docs/git-log)

For large checkouts, sparse checkout and partial clone address different costs. Sparse checkout limits the working-tree paths present locally. A partial clone using a filter such as `blob:none` can defer downloading file contents until needed, when supported by the server. Neither feature removes everyone else's commits from the repository's history. [5](https://git-scm.com/docs/git-sparse-checkout) [6](https://git-scm.com/docs/git-clone)

I would test these with the actual build workflow before recommending them to the whole team. A convenient small checkout stops being convenient if code generation expects missing directories or a build immediately downloads everything anyway.

More commits also do not automatically mean more conflicts. Edits to independent files often merge cleanly. The difficult cases deserve attention of their own: shared configuration, lockfiles, generated outputs, and changes that cross the same interfaces.

## Share standards without forcing identical tooling

Six languages need consistent expectations. They do not need the same formatter or the same test runner.

A small common set of requirements would be my starting point: an obvious build command, a test entry point, a named owner, dependency update rules, and a documented release path. Each language can meet those requirements with tools that suit it.

Shared configuration needs ownership too. A change to a root hook, base image, or code generator can affect people who never touch its directory. Someone should understand that reach and be responsible for reviewing changes to it.

CODEOWNERS can help route reviews. On GitHub, requiring approval from code owners is a separate branch protection setting; simply adding the file does not enforce that approval. [7](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

I would prefer a few enforced expectations with clear owners over a long standards document that depends on everyone remembering to read it.

## One commit still has to survive several releases

The biggest limit of the integration benefit appears after merging.

A backend service, a plugin, and a web application can be correct together in one commit and still reach their users at different times. A plugin may remain on an older version while the backend moves forward. A rollback can bring an older consumer back into use.

This is why I would make release compatibility part of the contract review.

Protocol Buffers gives concrete examples: adding fields can be safe for binary wire compatibility, while reusing field numbers is dangerous. It also distinguishes binary compatibility from source-level and application concerns. Successful parsing does not prove that two versions agree on meaning. [8](https://protobuf.dev/programming-guides/proto3/#updating)

For an illustrative change from `timeout_seconds` to `timeout_ms`, I would introduce the new field alongside the old one and define which value takes precedence. Readers would learn the new field while still accepting the old representation. Writers would keep supporting older consumers during the transition. Removal would wait until the supported version combinations no longer need the old field.

Those tests need rollback combinations too. Testing only the newest producer with the newest consumer misses the period when releases overlap.

Release records should make that overlap visible: which artifact was deployed, which commit produced it, and which contract versions it supports. If the release process changes, that information should remain easy to find.

Sharing a Git repository is a weak reason to release every component together. When two components depend on being released in a particular order, that dependency needs to be explicit.

## What I would keep

I would keep the ability to follow an integration change across the system in one place. It helped when models and DTOs changed, and it reduced the chance of leaving a consumer behind.

I would spend more effort on the costs that arrive every day: broad test selection, heavy base layers, long hooks, noisy history, and release tracking. Those are easy to postpone because each one looks manageable on its own.

Together, they shape how pleasant the repository is to work in.

The question I would bring to the next monorepo is simple: when one small thing changes, how much of the system should a developer have to think about?

I want the rest to remain available when I need it. I don't want every edit to require understanding all of it.

## Sources

1. [Pants: Using Pants in CI](https://www.pantsbuild.org/stable/docs/using-pants/using-pants-in-ci).
2. [pre-commit: Configuration, file filtering, and hook stages](https://pre-commit.com/).
3. [Bazel: Remote Caching](https://bazel.build/remote/caching).
4. [Git: git-log](https://git-scm.com/docs/git-log).
5. [Git: git-sparse-checkout](https://git-scm.com/docs/git-sparse-checkout).
6. [Git: git-clone, including partial-clone filters](https://git-scm.com/docs/git-clone).
7. [GitHub: About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).
8. [Protocol Buffers: Updating a proto3 message type](https://protobuf.dev/programming-guides/proto3/#updating).

---

*I'm Burak Hamuryen, a software engineer in Berlin working on distributed systems and real-time video infrastructure. More at [hamuryen.com](https://hamuryen.com).*
