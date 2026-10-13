---
name: suggestion
description: Generate 7-12 high-impact, ranked, context-specific ideas with quick-win/effort tags. Use when the user explicitly asks for suggestions, ideas, brainstorming, or improvement recommendations for a design, feature, architecture, or task.
disable-model-invocation: true
---

# Suggestion Mode

Generate valuable, ranked suggestions tailored to the current request. This skill loads only when explicitly named.

## Activation

Enable Suggestion Mode only when it is likely to improve the outcome. Do **not** force suggestions into every response.

Examples where it is useful:

- Designing or implementing software
- Reviewing architecture or infrastructure
- Planning features or workflows
- Debugging or troubleshooting
- Creating documentation
- Building automation
- Improving UX or developer experience
- Optimizing performance, reliability, or maintainability

Skip suggestions when they would add noise or are unrelated to the user's goal.

## Context-Gathering Phase

Before generating suggestions, assess whether the current request provides enough context to produce high-quality, specific ideas.

If the user's request is **vague, underspecified, or missing key details** (e.g. "give me ideas to improve this app", "suggestions for the project"), ask **3 to 5 clarifying questions** before generating suggestions.

If the request is already **specific and detailed enough** (e.g. includes concrete pain points, current architecture, or explicit constraints), skip the questions and proceed directly to generation.

Always check the codebase first (search and read relevant files) before asking — do not ask for information the agent can infer from existing code or docs.

### Question format

Use this structure for each question:

```markdown
**N. [Short question]**

- **a)** [Option text]
- **b)** [Option text] *(default)*
- **c)** [Option text]
```

Rules:

- Exactly three options per question: **a**, **b**, **c** only.
- Mark the default with `*(default)*` on that line (usually the safest or most common choice).
- Keep option text concrete; avoid overlap between a/b/c.
- If a question truly needs free text, still offer a/b/c and add: "Or reply with your own wording."

### Questioning guidelines

- Focus on **constraints** (time, budget, complexity tolerance), **scope** (what area to focus on), and **priorities** (reliability vs speed vs cost).
- Present all questions together in a single block, then wait for the user's answers before generating suggestions.
- Number questions sequentially from 1.

## Suggestion Rules

- Include suggestions only when genuinely useful.
- Generate **7-12** suggestions (never more than 12).
- Rank suggestions by **expected value** from highest to lowest.
- Every suggestion must be **specific to the current request and context**.
- Avoid generic advice or obvious best practices.
- Prefer concrete, actionable ideas over vague recommendations.

## Category Mix

Suggestions should cover a balanced mix of topics when relevant, including:

- New functionality
- User experience improvements
- Developer experience
- Automation
- Performance optimization
- Reliability and fault tolerance
- Security
- Observability and monitoring
- Documentation
- Maintainability and refactoring
- Cost reduction
- Scalability
- Integrations
- Testing and validation
- Operational workflows
- Creative experiments

Not every category must appear every time, but vary the ideas to maximize usefulness.

## Inspiration Rule

At least **2 suggestions** should be inspired by successful products, platforms, or industry patterns. Explicitly name the inspiration when doing so.

Examples: GitHub Checks, Linear Workflows, Stripe Idempotency, Notion Slash Commands, VS Code Command Palette, Figma Multiplayer, Obsidian Backlinks, GitHub Actions, Cursor Composer, Claude Artifacts, Raycast Extensions.

Adapt the underlying concept rather than copying the implementation.

## Creativity Rule

At least **2 suggestions** should be intentionally creative or unconventional. They may explore surprising workflows, novel interfaces, AI-assisted behaviors, or experimental product ideas, provided they remain relevant to the current context.

## Quick Win Tagging

Every suggestion gets a visual tag based on a 2-axis matrix: **impact** (1-5) × **effort** (Low/Medium/High).

### Impact scale

- **1 – Marginal:** nice to have, barely noticeable
- **2 – Minor:** small improvement for a niche scenario
- **3 – Moderate:** noticeable quality-of-life improvement
- **4 – High:** meaningful productivity/reliability/UX gain
- **5 – Transformative:** changes how you work, unlocks new capabilities

### Tag matrix

| Effort →<br>↓ Impact | Low | Medium | High |
|----------------------|-----|--------|------|
| **5 – Transformative** | 🟢 Quick win | 🔵 Strategic | 🔵 Strategic |
| **4 – High**          | 🟢 Quick win | 🔵 Strategic | 🔵 Strategic |
| **3 – Moderate**      | 🟡 Nice-to-have | 🔵 Strategic | ⚪ Skip |
| **2 – Minor**         | 🟡 Nice-to-have | 🟡 Nice-to-have | ⚪ Skip |
| **1 – Marginal**      | 🟡 Nice-to-have | ⚪ Skip | ⚪ Skip |

### Rules

- Suggestions tagged ⚪ Skip should **not** appear in the final output — they are low impact for high cost.
- If a suggestion would be ⚪ Skip, discard it and generate a replacement.
- After tagging, verify the final list has at least 2 🟢 Quick wins — if not, re-evaluate impact scores or generate new candidates.

## Output Format

Present suggestions as a numbered list (1. 2. 3. ...). Numbering must be sequential starting from 1, so the user can easily reference "number 3", "the 5th one", etc.

For each suggestion include:

- **[Tag]** **Title**
- **Short rationale** explaining the expected value
- **Impact:** 1–5 · **Difficulty:** Low / Medium / High

Keep each suggestion concise while remaining specific enough to be actionable.

### Output example

```markdown
1. 🟢 **Add healthcheck endpoint**
   Stop guessing whether the service is alive. A GET /health tells you in 1s.
   **Impact:** 5 · **Difficulty:** Low

2. 🔵 **Migrate config to environment variables**
   Remove hardcoded values from config. Fewer errors when moving between environments.
   **Impact:** 4 · **Difficulty:** Medium
```

## Pitfalls

- **Empty suggestions when context is missing:** Explore the codebase (search and read relevant files) before generating. If context is thin, gather it first with clarifying questions.
- **Wrong suggestion count:** Verify the final list has 7-12 items. If under range, add creative or inspiration-driven ideas to fill gaps. If over 12, trim the lowest-expected-value ideas.
- **Overly generous impact scores:** If most suggestions score 4–5 by default, recalibrate — only truly transformative or high-value improvements earn those scores. A moderate QoL bump is a 3, not a 4.
- **⚪ Skip suggestions leaking through:** After tagging, verify no ⚪ Skip suggestions made it to the final list. High effort + low impact ideas should be discarded before output.

## Goal

Surface ideas the user may not have considered, prioritizing high-impact improvements that meaningfully enhance the current project, design, or task. When context is thin, gather it first with targeted clarifying questions — better context yields better suggestions.
