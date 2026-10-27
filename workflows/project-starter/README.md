# Project Starter — From Idea to Implementation Plan

A lightweight, reusable workflow for defining **any software or infrastructure project** with an LLM: a quick experiment, POC, MVP, production service, CLI, web application, automation, or homelab project.

**Guiding principle: Simple > Clever.** Define only what matters for the project's actual scope and maturity. Avoid premature architecture, infrastructure, and process.

## Files

| File | Purpose |
| --- | --- |
| [`PROJECT_CHECKLIST.md`](PROJECT_CHECKLIST.md) | 150 categorized questions to help you think through a project. Answer only what you know. |
| [`PROJECT_INTERVIEWER.md`](PROJECT_INTERVIEWER.md) | Reusable prompt for an interactive requirements interview. Produces functional and technical specifications. |
| [`PROJECT_PLANNER.md`](PROJECT_PLANNER.md) | Reusable prompt that turns the two specifications into an actionable implementation plan. |

This README is a guide, not an additional prompt you need to run.

## Workflow

```text
Your idea + optional checklist answers
                |
                v
      PROJECT_INTERVIEWER.md
                |
         Q&A, in rounds
                |
                v
      FUNCTIONAL_SPEC.md
       TECHNICAL_SPEC.md
                |
                v
        PROJECT_PLANNER.md
                |
                v
      IMPLEMENTATION_PLAN.md
                |
                v
       Coding agent / developer
```

## Step 1 — Capture your idea (optional checklist)

Open `PROJECT_CHECKLIST.md`. Fill in as much or as little as you want. You can use numbered answers or plain language. The labels mean:

- **[CORE]**: generally worth defining.
- **[COND]**: answer only when applicable.
- **[ADV]**: for projects that need extra depth.

Use `?` for **unknown**, `N/A` for **not applicable**, and `LATER` for **decide later**. Keep **confirmed decisions**, **negotiable preferences**, and **non-negotiable constraints** distinct.

Example:

```md
# My project
Idea: A small CLI that renames downloaded files using configurable rules.

## Checklist answers
11: POC
13: CLI
31: Preview changes, rename files, undo a rename
51: Preference: Python
55: Constraint: Linux
121: Constraint: $0

## Non-negotiable constraints
- Never overwrite existing files.

## Questions / unknowns
- Not sure how configuration should be stored.
```

You **do not need to finish the checklist** before continuing.

## Step 2 — Run the interview

Start a new conversation with your preferred LLM. Provide:

1. `PROJECT_INTERVIEWER.md` as the instructions to follow.
2. Your idea and any initial specifications.
3. Your checklist answers, or the full `PROJECT_CHECKLIST.md` if you want the model to use it as a reference.

Example message:

> Follow the instructions in PROJECT_INTERVIEWER.md. My idea is a CLI that renames downloaded files. Here are my initial checklist answers: [paste answers]. Ask me questions in rounds and generate the two specifications when we are done.

The interviewer will ask **1–5 numbered questions per round**, offer options such as `a/b/c/d`, recommend pragmatic defaults when appropriate, and avoid asking what you have already answered. You can respond compactly, for example: `1b 2d 3a`.

When the major decisions are clear, it will ask whether to continue exploring or generate the deliverables. You can also ask to finish early and keep unknowns explicitly marked.

### Interview outputs

- **`FUNCTIONAL_SPEC.md`** — **what** the project should do: goals, users, scope, workflows, requirements (`FR-xx`), business rules, and acceptance criteria.
- **`TECHNICAL_SPEC.md`** — **how it is constrained technically**: confirmed decisions (`DEC-xx`), preferences, stack, environment, non-functional requirements (`NFR-xx`), risks, and open questions.

Save both files. They must stand on their own: the next model should not need the interview conversation.

## Step 3 — Generate the implementation plan

Start a **separate conversation**, ideally with the model you want to use for planning. Provide:

1. `PROJECT_PLANNER.md` as the instructions to follow.
2. The generated `FUNCTIONAL_SPEC.md`.
3. The generated `TECHNICAL_SPEC.md`.
4. Optionally, repository context if the project already exists.

Example message:

> Follow PROJECT_PLANNER.md. Read FUNCTIONAL_SPEC.md and TECHNICAL_SPEC.md in full, then generate IMPLEMENTATION_PLAN.md. Respect confirmed decisions, avoid overengineering, and ask only about real blockers.

The planner should generate **`IMPLEMENTATION_PLAN.md`** with small phases, concrete tasks (`TASK-xx`), dependencies, acceptance criteria, risks, and a requirements-to-tasks coverage matrix. It **does not write implementation code**.

## Step 4 — Implement

Give `IMPLEMENTATION_PLAN.md` (and preferably both specifications) to a coding agent or developer. Work through the tasks in dependency order, verify acceptance criteria, and keep the specifications updated when requirements change.

The three starter files are **reusable templates**. Keep them unchanged for each project; store the generated specifications and plan in that project's repository or documentation folder.

## Suggested project folder

```text
my-project/
└── docs/
    └── project/
        ├── FUNCTIONAL_SPEC.md
        ├── TECHNICAL_SPEC.md
        └── IMPLEMENTATION_PLAN.md
```

## Key rules

- **Start small.** An experiment does not need production-grade infrastructure.
- **Never invent requirements.** Mark assumptions and open questions clearly.
- **Respect confirmed decisions and constraints.** Recommendations are not approvals.
- **Avoid repeated questions.** Use the context already provided.
- **Defer low-impact decisions.** Not everything must be decided before coding.
- **Keep responsibilities separate.** Interviewer = requirements; Planner = tasks; Coding agent = implementation.
- **Replan when needed.** If requirements change, update the two specifications and rerun the planner rather than repeating the whole interview.

## Quick start

1. Describe your idea (optionally fill out part of `PROJECT_CHECKLIST.md`).
2. Run `PROJECT_INTERVIEWER.md` with your idea and answers.
3. Save `FUNCTIONAL_SPEC.md` and `TECHNICAL_SPEC.md`.
4. Run `PROJECT_PLANNER.md` with those two files.
5. Save `IMPLEMENTATION_PLAN.md` and start implementation.

**No special tools or paid services are required** beyond an LLM that can read the prompts and produce Markdown.
