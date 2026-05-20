# Amazonian Agent Skills

A small, opinionated suite of agent skills that translates Amazon operational mechanisms — PRFAQ, six-page narratives, Weekly Business Reviews, Correction of Errors, mechanism design, and Leadership Principles review — into composable, inspectable agent workflows.

The point: turn good judgment into repeatable mechanisms. Not vibes. Not "think strategically." Mechanisms with gates, schemas, checks, and audit trails.

> This project is not affiliated with or endorsed by Amazon.com, Inc. It is an unofficial, community-built skills pack inspired by publicly described practices.

## Why these skills exist

> Mechanisms make bad thinking expensive *before* bad execution becomes expensive.

Most agent skills tell the model to "be thoughtful." That is not a mechanism; that is a vibe. The skills in this suite refuse to emit output if the inputs are vague, tag claims with `[assumption]` when evidence is thin, and hand off to the next skill in a deterministic chain.

## The operating chain

```text
            Idea / Problem
                  │
                  ▼
     working-backwards-prfaq
                  │
                  ▼
     amazon-writing-linter
                  │
                  ▼
 leadership-principles-reviewer
                  │
                  ▼
      mechanism-designer
                  │
                  ▼
       six-page-narrative
                  │
                  ▼
            decision gate
                  │
                  ▼
    weekly-business-review
                  │
                  ▼
     correction-of-errors
   (when reality starts chewing furniture)
```

## Suite contents

| # | Skill | Purpose |
|---|-------|---------|
| 01 | [`working-backwards-prfaq`](skills/01-working-backwards-prfaq/SKILL.md) | Turn an idea into a PRFAQ packet |
| 02 | [`amazon-writing-linter`](skills/02-amazon-writing-linter/SKILL.md) | Strip vague adjectives, unsupported claims, weasel words; surface decisions and owners |
| 03 | [`six-page-narrative`](skills/03-six-page-narrative/SKILL.md) | Convert a strategy or architecture into a decision memo with risks, alternatives, and dissent |
| 04 | [`mechanism-designer`](skills/04-mechanism-designer/SKILL.md) | Convert a goal into a recurring operational mechanism with cadence, inputs, inspection, and escalation |
| 05 | [`weekly-business-review`](skills/05-weekly-business-review/SKILL.md) | Generate a WBR from metrics with required variance analysis |
| 06 | [`correction-of-errors`](skills/06-correction-of-errors/SKILL.md) | Run a blameless post-incident review using Five Whys, with action items and owners |
| 07 | [`leadership-principles-reviewer`](skills/07-leadership-principles-reviewer/SKILL.md) | Evaluate a proposal against Amazon-style leadership principles, surfacing contradictions and hidden risk |

Every skill in this suite conforms to [`SKILL_DESIGN_PATTERN.md`](SKILL_DESIGN_PATTERN.md).

## Install

Skills follow the standard Cursor and Claude `SKILL.md` convention. To use them locally:

```bash
# Personal scope (available across all your projects)
mkdir -p ~/.cursor/skills
cp -R skills/* ~/.cursor/skills/

# Or project scope (shared with the repo)
mkdir -p .cursor/skills
cp -R skills/* .cursor/skills/
```

Once installed, the agent will discover skills by description. You can also invoke explicitly:

```text
Use the working-backwards-prfaq skill to draft a PRFAQ for <idea>.
```

## Composition

Skills are designed to chain. The output of one is structured input to the next. Example flow:

1. `working-backwards-prfaq` emits a decision packet with `success_metrics`.
2. `mechanism-designer` consumes those metrics to define the recurring inspection.
3. `weekly-business-review` runs that inspection on cadence.
4. `correction-of-errors` fires when a metric breaches threshold.
5. Findings feed back into the next PRFAQ.

This is the operating system, not seven unrelated prompts.

## What this suite is not

- A management cult.
- A blanket endorsement of any particular company culture.
- A magic productivity layer.
- A replacement for talking to the actual customer.

These are mechanisms for *thinking visibly in writing*. They make bad reasoning expensive in a forum where it is cheap to fix.

## Repo layout

```text
amazonian/
├── README.md
├── LICENSE
├── SKILL_DESIGN_PATTERN.md
└── skills/
    ├── 01-working-backwards-prfaq/
    │   ├── SKILL.md
    │   ├── templates/prfaq-template.md
    │   └── examples/example-prfaq.md
    ├── 02-amazon-writing-linter/
    │   ├── SKILL.md
    │   └── rules.yaml
    ├── 03-six-page-narrative/
    │   ├── SKILL.md
    │   └── template.md
    ├── 04-mechanism-designer/
    │   ├── SKILL.md
    │   └── mechanism-template.md
    ├── 05-weekly-business-review/
    │   ├── SKILL.md
    │   ├── wbr-template.md
    │   └── examples/example-wbr.md
    ├── 06-correction-of-errors/
    │   ├── SKILL.md
    │   ├── coe-template.md
    │   └── examples/example-coe.md
    └── 07-leadership-principles-reviewer/
        ├── SKILL.md
        └── rubric.yaml
```

The three worked examples (`example-prfaq.md`, `example-wbr.md`, `example-coe.md`) share a common hypothetical product ("ChangeLens") so you can read them in sequence and see how the artifacts chain.

## Contributing

Proposed skills must satisfy the spine in [`SKILL_DESIGN_PATTERN.md`](SKILL_DESIGN_PATTERN.md). The disqualifying criteria in that doc are the bar.

## License

MIT. See [`LICENSE`](LICENSE).

## Disclaimer

"Amazon", "AWS", "Working Backwards", and the Amazon Leadership Principles are property of Amazon.com, Inc. This project is an independent interpretation of publicly described practices and is not affiliated with, endorsed by, or sponsored by Amazon.
