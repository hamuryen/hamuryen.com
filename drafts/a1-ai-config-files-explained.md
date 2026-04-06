# Every AI Config File Explained: What Goes Where and Why

*CLAUDE.md, AGENTS.md, .cursorrules, settings.json, rules/, .mcp.json. If you've lost track of which file does what, you're not alone.*

---

A teammate asked me where to put a coding rule so Claude would follow it every time. I paused. I knew about CLAUDE.md. I'd heard of AGENTS.md. I vaguely remembered something about a rules directory. I wasn't sure which one to use, or if they even did different things.

Then I looked around and realized the ecosystem has accumulated about a dozen configuration files across different tools, and nobody has a clear picture of what goes where. Cursor has .cursorrules (now deprecated) and .cursor/rules/. Claude Code has CLAUDE.md and .claude/rules/ and settings.json and .mcp.json. There's AGENTS.md which claims to work everywhere. There's SKILL.md for skills. There are local variants of almost everything.

Here's what I found.

## The Quick Reference

Here's every file you might encounter, what it does, and who reads it:

| File | What it does | Who reads it | Goes in git? |
|------|-------------|-------------|-------------|
| **CLAUDE.md** | Project instructions for Claude | Claude Code only | Yes |
| **CLAUDE.local.md** | Your personal project overrides | Claude Code only | No |
| **~/.claude/CLAUDE.md** | Your global instructions (all projects) | Claude Code only | No |
| **AGENTS.md** | Universal agent instructions | Cursor, Copilot, Codex, Jules, 25+ tools | Yes |
| **.cursorrules** | Cursor-specific rules (legacy) | Cursor only | Yes |
| **.cursor/rules/** | Cursor-specific rules (current) | Cursor only | Yes |
| **.claude/rules/*.md** | Modular, path-scoped rules | Claude Code only | Yes |
| **~/.claude/rules/*.md** | Your global rules (all projects) | Claude Code only | No |
| **.claude/settings.json** | Permissions, hooks, env vars | Claude Code only | Yes |
| **.claude/settings.local.json** | Your local settings overrides | Claude Code only | No |
| **~/.claude/settings.json** | Your global settings | Claude Code only | No |
| **.mcp.json** | MCP server connections (project) | Claude Code only | Yes |
| **~/.claude/.mcp.json** | MCP server connections (global) | Claude Code only | No |
| **.claude/skills/*/SKILL.md** | On-demand domain knowledge | Claude Code only | Yes |
| **.claude/agents/*.md** | Custom subagent definitions | Claude Code only | Yes |

Looks like a lot. In practice, most of them fall into three buckets: **instructions** (what Claude should know), **configuration** (what Claude can do), and **integrations** (what Claude can connect to).

## The Big Confusion: CLAUDE.md vs AGENTS.md

Short version:

**CLAUDE.md** is read by Claude Code. Only Claude Code. If your entire team uses Claude Code, this is all you need.

**AGENTS.md** is an open standard adopted by the [Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) (a Linux Foundation project co-founded by Anthropic, OpenAI, and Block, with Google, Microsoft, and AWS as platinum members). It's read by 25+ tools: Cursor, GitHub Copilot, Codex, Jules, Gemini CLI, and more. Over 60,000 repositories on GitHub already have one.

**If your team uses different AI tools, use AGENTS.md as the shared baseline and add CLAUDE.md for Claude-specific things.**

You can import AGENTS.md into CLAUDE.md so you don't duplicate rules:

```markdown
# CLAUDE.md
@AGENTS.md

# Claude-specific additions
- Use plan mode for database migrations
- Run tests with `npm test -- --watchAll=false`
```

Claude Code reads the imported file at session start along with the rest.

**.cursorrules** is Cursor's legacy format. It still works but Cursor themselves recommend migrating to .cursor/rules/ for new projects, or better yet, AGENTS.md for cross-tool compatibility.

## CLAUDE.md: The Instructions File

CLAUDE.md is where you tell Claude how to behave in your project. Think of it as a system prompt that persists across every session.

### Where it lives

CLAUDE.md can exist at multiple levels, and all of them get loaded:

```
~/.claude/CLAUDE.md          ← global (all projects, all sessions)
../../CLAUDE.md               ← grandparent directory
../CLAUDE.md                  ← parent directory
./CLAUDE.md                   ← project root (shared with team)
./CLAUDE.local.md             ← project root (personal, gitignored)
./src/CLAUDE.md               ← subdirectory (loaded on demand)
./src/api/CLAUDE.md           ← deeper subdirectory (loaded on demand)
```

Files in parent directories and the project root load at session start. Files in subdirectories load on demand when Claude reads files in those directories. Your personal `CLAUDE.local.md` loads last, so it can override team rules.

### What to put in it

The official guidance from Anthropic is clear: for each line, ask *"Would removing this cause Claude to make mistakes?"* If not, cut it.

**Good candidates:**

```markdown
# Build & Test
- Build: `npm run build`
- Test single file: `npm test -- path/to/test`
- Lint: `npm run lint`

# Code Style
- Use ES modules (import/export), not CommonJS (require)
- Prefer named exports over default exports
- Error messages should be user-facing, not developer-facing

# Git
- Branch naming: feature/ticket-number-short-description
- Commit messages: imperative mood, under 72 chars
- Never force push to main
```

**Bad candidates (remove these):**
- Anything Claude already does correctly without being told
- Standard language conventions (Claude knows how Python or TypeScript work)
- Detailed API documentation (link to docs instead)
- Long tutorials or explanations
- Things that change frequently

### The size trap

Boris Cherny, the creator of Claude Code, [shared his setup publicly](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/). Most developers write 500+ line CLAUDE.md files. His is about 100 lines. And it works better than the long ones.

Why? Because LLM performance degrades with context length. A bloated CLAUDE.md means Claude is more likely to miss the one rule that actually matters. More instructions can actually lead to worse adherence.

**My rule of thumb: if your CLAUDE.md is over 200 lines, split it up.** Use .claude/rules/ for modular rules (explained below) or @import to pull in separate files.

### The @import trick

You can reference other files from CLAUDE.md:

```markdown
# CLAUDE.md
See @README.md for project overview.
See @docs/api-conventions.md for API design rules.

@AGENTS.md
```

This keeps CLAUDE.md short while still giving Claude access to detailed docs when it needs them.

## .claude/rules/ : Modular and Path-Scoped Rules

When your CLAUDE.md gets too long, or when you want rules that only apply to certain files, use the rules directory.

### Unconditional rules

Files in `.claude/rules/` without a `paths` field load at session start, just like CLAUDE.md:

```markdown
# .claude/rules/testing.md
- Always run tests after code changes
- Prefer integration tests over unit tests for API endpoints
- Never mock the database in integration tests
```

### Path-scoped rules

Add a `paths` field in the frontmatter and the rule only loads when Claude touches matching files:

```markdown
# .claude/rules/react-components.md
---
paths:
  - "src/components/**/*.tsx"
  - "src/hooks/**/*.ts"
---

- Use function components, never class components
- Extract shared logic into custom hooks
- Props type goes in the same file, above the component
```

```markdown
# .claude/rules/api-routes.md
---
paths:
  - "src/api/**/*.ts"
---

- Every endpoint must validate input with zod
- Return consistent error format: { error: string, code: number }
- Log request/response for non-GET endpoints
```

In a monorepo, this means backend rules don't pollute the context when Claude is working on the frontend.

### Directory structure example

```
.mcp.json                           # MCP server connections (project root)
.claude/
├── CLAUDE.md                    # Short, high-level project rules
├── settings.json                # Permissions, hooks, env vars
├── rules/
│   ├── code-style.md            # Loads every session
│   ├── git-conventions.md       # Loads every session
│   ├── frontend/
│   │   ├── react.md             # paths: src/components/**
│   │   └── styling.md           # paths: src/styles/**
│   └── backend/
│       ├── api.md               # paths: src/api/**
│       └── database.md          # paths: src/models/**
├── skills/
│   └── fix-issue/
│       └── SKILL.md             # Invoked with /fix-issue
└── agents/
    └── security-reviewer.md     # Custom subagent
```

## settings.json: The Enforcement Layer

**CLAUDE.md is advisory. settings.json is enforced.** Big difference.

Claude follows CLAUDE.md instructions about 80% of the time. It's an LLM reading context, not a machine executing rules. If you write "never edit .env files" in CLAUDE.md, Claude will usually respect it. Usually.

settings.json is deterministic. 100%. If you deny file edits to `.env` in settings.json, Claude physically cannot edit that file.

### Permissions

Control what Claude can and can't do:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git commit *)",
      "Read",
      "Edit"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force *)",
      "Edit(/.env)",
      "Edit(package-lock.json)"
    ]
  }
}
```

If denied at any level, it's denied. You cannot allow at a lower scope to override a deny from a higher scope.

### Hooks (the "100% enforcement" trick)

Hooks are scripts that run automatically at specific points in Claude's workflow. This is how you guarantee something happens every time:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATH"
          }
        ]
      }
    ]
  }
}
```

This runs Prettier after every file edit. Not sometimes. Every time.

Other useful hook patterns:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --fix $CLAUDE_FILE_PATH"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if echo $CLAUDE_FILE_PATH | grep -q 'migrations/'; then echo 'BLOCKED: Do not auto-edit migration files' >&2; exit 1; fi"
          }
        ]
      }
    ]
  }
}
```

The mental model: **CLAUDE.md for guidelines, hooks for guardrails.**

### Environment variables

```json
{
  "env": {
    "NODE_ENV": "development",
    "DATABASE_URL": "postgres://localhost/mydb"
  }
}
```

Put secrets in `.claude/settings.local.json` (gitignored), not in the shared settings file.

### Scope and precedence

Settings merge from multiple levels. Higher scopes win:

1. **Managed settings** (organization IT, cannot override)
2. **.claude/settings.local.json** (your personal overrides)
3. **.claude/settings.json** (team/project)
4. **~/.claude/settings.json** (your global defaults)

## .mcp.json: External Tool Connections

MCP (Model Context Protocol) lets Claude interact with external services. The configuration lives in `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN"
      }
    }
  }
}
```

Project-level `.mcp.json` goes in the project root (shared with team). Personal MCP configs go in `~/.claude/.mcp.json`.

## Skills and Subagents

Two more file types:

### Skills (.claude/skills/*/SKILL.md)

Skills are on-demand knowledge that Claude loads only when relevant, keeping your main context clean:

```markdown
# .claude/skills/deploy/SKILL.md
---
name: deploy
description: Production deployment workflow
---

1. Run full test suite: `npm test`
2. Build production bundle: `npm run build`
3. Deploy to staging: `npm run deploy:staging`
4. Run smoke tests: `npm run test:smoke`
5. Deploy to production: `npm run deploy:prod`
```

Invoke with `/deploy` in Claude Code. Unlike CLAUDE.md, this doesn't load every session.

Claude Code also ships with **bundled skills** that work out of the box: `/simplify` refactors selected code for clarity, `/review` does a code review, `/debug` investigates failing tests, `/batch` runs the same change across multiple files, `/loop` runs a command repeatedly until it passes. These aren't slash commands like `/clear` or `/compact` (which are built-in functions). They're pre-written prompt templates that load context and run multi-step workflows. You can see the full list with `/skills`.

### Subagents (.claude/agents/*.md)

Custom agents that run in isolated context:

```markdown
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---

You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
```

Tell Claude: "Use the security-reviewer subagent to review this PR." The subagent runs in its own context window and reports back, keeping your main conversation clean.

## The Decision Tree

Not sure where to put something? Follow this:

**"I want all AI tools to follow this rule"**
→ AGENTS.md

**"I want Claude to follow this rule in every session"**
→ CLAUDE.md (if short and universally applicable)
→ .claude/rules/*.md (if you want modularity)

**"I want Claude to follow this rule only for certain files"**
→ .claude/rules/*.md with `paths` frontmatter

**"I want this rule enforced 100%, no exceptions"**
→ .claude/settings.json (permissions for blocking, hooks for automation)

**"I want this rule only for me, not my team"**
→ CLAUDE.local.md (instructions) or .claude/settings.local.json (config)

**"I want this rule across all my projects"**
→ ~/.claude/CLAUDE.md (instructions) or ~/.claude/settings.json (config)

**"I want Claude to connect to an external service"**
→ .mcp.json

**"I want on-demand workflows Claude can invoke"**
→ .claude/skills/*/SKILL.md

## Setting Up for a Team

Say your team has 5 engineers. Three use Claude Code, two use Cursor. Everyone should follow the same coding standards.

**Step 1: Create AGENTS.md with shared rules**

```markdown
# AGENTS.md

## Build
- Install: `npm install`
- Test: `npm test`
- Lint: `npm run lint`

## Code Style
- TypeScript strict mode
- Use camelCase for variables, PascalCase for types
- Prefer named exports

## Git
- Branch: feature/JIRA-123-short-description
- Commits: imperative mood, reference ticket number
```

This covers Cursor, Copilot, Codex, and any other tool your team might adopt.

**Step 2: Create CLAUDE.md importing AGENTS.md**

```markdown
# CLAUDE.md
@AGENTS.md

# Claude-specific
- Use plan mode for changes touching 3+ files
- Run `npm test` after code changes
- Never edit files in /migrations without asking first
```

**Step 3: Add enforcement via settings.json**

```json
{
  "permissions": {
    "deny": [
      "Edit(/.env*)",
      "Bash(git push --force *)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $CLAUDE_FILE_PATH"
          }
        ]
      }
    ]
  }
}
```

**Step 4: Tell team members to create personal files**

Each engineer creates their own `CLAUDE.local.md`:

```markdown
# CLAUDE.local.md (gitignored)
- I prefer concise responses
- My local API runs on port 3001
```

And `.claude/settings.local.json` for secrets:

```json
{
  "env": {
    "API_KEY": "your-personal-key"
  }
}
```

**Commit to git:** AGENTS.md, CLAUDE.md, .claude/settings.json, .claude/rules/
**Gitignore:** CLAUDE.local.md, .claude/settings.local.json

## Auto Memory: Claude's Own Notes

You write CLAUDE.md. But Claude also writes its own notes.

Auto memory is on by default. When Claude notices something worth remembering (a build command that works, a debugging pattern, a preference you expressed), it saves a note to `~/.claude/projects/<project>/memory/`. These notes load at the start of every session, just like CLAUDE.md.

The memory directory looks like this:

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          # Index file, loaded every session (first 200 lines)
├── debugging.md       # Detailed notes on debugging patterns
├── api-conventions.md # API decisions Claude learned
└── user-preferences.md
```

`MEMORY.md` is the entry point. The first 200 lines (or 25KB) load at session start. Claude keeps it concise by moving details into separate topic files that it reads on demand.

### How it works in practice

You correct Claude: "don't use default exports, we use named exports here." Claude remembers that correction for future sessions without you adding it to CLAUDE.md. You mention "tests require Redis running locally," it saves that too.

The key difference from CLAUDE.md: auto memory is personal and local. It doesn't sync across machines or team members. If you want something shared, put it in CLAUDE.md. If it's something Claude learned while working with you, let auto memory handle it.

Run `/memory` to see what's stored, toggle it on/off, or edit files directly. Everything is plain markdown.

## A Note on Session Management

Config files only work if the context window isn't full of noise. Use `/clear` between unrelated tasks, `/compact` when context is getting full but you're not done, and name your sessions (`claude -n auth-refactor`) so you can resume later. The details of effective session management are a separate topic from configuration.

## Your Global Setup (~/.claude/)

Everything in `~/.claude/` applies to all your projects on this machine. This is where your personal preferences live.

```
~/.claude/
├── CLAUDE.md              # Your global instructions
├── settings.json          # Your global settings
├── .mcp.json              # Your global MCP connections
├── rules/
│   ├── preferences.md     # Your coding preferences
│   └── workflows.md       # Your preferred workflows
├── keybindings.json       # Custom keyboard shortcuts
└── projects/
    └── <project>/
        └── memory/        # Auto memory (per project)
            └── MEMORY.md
```

### Global CLAUDE.md example

```markdown
# ~/.claude/CLAUDE.md

# Personal Preferences
- Keep responses concise
- Don't add comments to code unless the logic is non-obvious
- Don't add docstrings unless I ask

# Git
- Never add Co-Authored-By lines to commit messages
- Commit messages in English

# Code Style
- Prefer functional patterns over classes where possible
- No unnecessary abstractions
```

These apply everywhere: personal projects, work repos, open source contributions.

### Global settings

```json
// ~/.claude/settings.json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf /)",
      "Edit(~/.ssh/*)"
    ]
  },
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude needs attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

That notification hook saves you from staring at the terminal waiting for Claude to finish.

## Common Mistakes

**Putting permissions in CLAUDE.md.** Writing "never edit .env" in CLAUDE.md is a suggestion. Putting it in settings.json deny list is a guarantee. Know the difference.

**Bloated CLAUDE.md.** If it's over 200 lines, Claude starts missing rules. Split into .claude/rules/ files or use @imports.

**Committing secrets.** API keys go in `.claude/settings.local.json`, not `.claude/settings.json`. Add the local file to .gitignore.

**Ignoring AGENTS.md.** If anyone on your team uses a tool other than Claude Code, you need AGENTS.md. Even if everyone uses Claude Code today, AGENTS.md is the safer long-term bet since it's tool-agnostic and backed by an industry foundation.

**Duplicating rules.** Don't write the same rule in AGENTS.md and CLAUDE.md. Import one from the other with `@AGENTS.md`.

**Not using hooks for critical rules.** If a rule must be followed 100% of the time (formatting, linting, security checks), make it a hook. CLAUDE.md is 80% adherence. Hooks are 100%.

---

## Further Reading

**Official Documentation:**
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [CLAUDE.md Documentation](https://code.claude.com/docs/en/memory)
- [Extend Claude Code (Skills, Hooks, MCP, Subagents)](https://code.claude.com/docs/en/features-overview)

**Standards:**
- [AGENTS.md Specification](https://agents.md/)
- [Agentic AI Foundation (Linux Foundation)](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)
- [Model Context Protocol](https://modelcontextprotocol.io/)

**Community:**
- [Claude Code Creator's 100-Line Workflow](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/)
- [Builder.io: 50 Claude Code Tips](https://www.builder.io/blog/claude-code-tips-best-practices)
- [Claude Code Ultimate Guide (GitHub)](https://github.com/FlorianBruniaux/claude-code-ultimate-guide)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
