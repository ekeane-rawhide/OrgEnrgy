# Scaffold code generation for full-stack ASP.NET systems

Direction chosen over: new language (rejected — ecosystem cost too high
for the actual problem), runtime config engine (rejected in favor of
this — generates real code you own instead of an interpreter you're
boxed into). Not yet built; this is the design to react to.

## Why scaffold-gen over the runtime engine

A runtime meta-model engine (ABP/Orchard-style: entities interpreted at
request time from stored definitions) gets you to a working CRUD app
fastest, but every customization fights the engine, and you're forever
coupled to its runtime. Code generation front-loads the same meta-model
work but emits real C#/Razor/EF Core files into the project — the
generator is a one-time (or re-run-on-change) step, not a permanent
dependency. Cost: no live schema editing without a re-gen + migration;
benefit: zero ceiling on customization, because generated code is just
code, editable and debuggable like anything else.

## The pipeline

    Meta-model definition (YAML/JSON)
      ↓
    Generator (CLI)
      ↓
    Emitted project files:
      - EF Core entity classes + DbContext + migrations
      - DTOs / request-response contracts
      - Repository or direct DbContext access layer
      - Minimal API endpoints (or MVC controllers)
      - Blazor or Razor Pages CRUD screens
      - Validation (FluentValidation or DataAnnotations)
      - Auth/permission attributes wired to scope
      ↓
    Developer edits generated code directly from here on

This reuses the primitives already defined for OrgEnrgy
(`ORG_CELL_CONTEXT.md` §"Engineering layer"): EntityDefinition,
FieldDefinition, RelationshipDefinition map directly onto EF Core
entities/properties/navigation properties. WorkflowDefinition and
FormDefinition map onto generated endpoint/page logic and Blazor forms,
respectively. The OU hierarchy maps onto scope-filtering code baked into
the generated query layer (a `WHERE OrgUnitId IN (@scope)` clause
generated once, not evaluated by an interpreter per request).

## Meta-model source format (sketch)

```yaml
entity: Client
  fields:
    - { name: FirstName, type: string, required: true }
    - { name: LastName,  type: string, required: true }
    - { name: DateOfBirth, type: date }
  relationships:
    - { name: Program, type: manyToOne, target: Program }
    - { name: Events,  type: oneToMany, target: Event }
  scope: OrgUnit
  forms:
    - { name: Intake, fields: [FirstName, LastName, DateOfBirth, Program] }
```

One file per entity (or one file, many entities) is the whole app
definition; the generator walks the set and emits the full vertical
slice per entity plus the cross-cutting DbContext/migration/auth wiring.

## Generator implementation choices

| Approach | Pros | Cons |
|---|---|---|
| **CLI + text templates** (Scriban/Handlebars, like `dotnet new` templates) | Simple, debuggable, language-agnostic template files, easy to iterate on output format | Generator is a separate build step, no compile-time feedback if template output is malformed |
| **Roslyn source generators** | Compile-time, IDE shows generated code live, no separate CLI step | Only good for code *inside* the C# compilation (entities, DTOs) — can't emit Razor/Blazor files or migrations this way |
| **T4 templates** | Native to .NET, mature | Clunky authoring experience, mostly legacy now |

Recommendation: **CLI + text templates** as the primary path (handles
the full vertical slice, including non-C# output like `.razor` and
migration SQL), with **Roslyn source generators** as an optional layer
later for the pure-C# pieces (DTOs, entity partial classes) so the IDE
shows live feedback without a re-gen step. Don't start with Roslyn —
it can't cover the whole surface and adds complexity before there's a
working baseline.

## What "easiest way to create full-stack systems" concretely means here

1. Developer writes/edits the YAML meta-model (or, later, a small UI
   over it — but text-first, so it's diffable and git-friendly from
   day one).
2. Runs `scaffold generate` → emits/updates entities, DbContext,
   migration, API, and CRUD UI for anything new or changed.
3. Developer edits generated code freely for the 20% custom cases;
   re-running the generator on an already-hand-edited file needs a
   strategy — partial classes / clearly marked generated-vs-custom
   file boundaries (generated files never hand-edited, custom logic
   goes in a sibling partial or override file) so regen doesn't clobber
   work. This is the single hardest design problem in the whole
   pipeline and needs to be solved before anything else, not after.

## Open questions before building anything

- Regeneration/merge strategy (above) — the make-or-break detail.
- Minimal API vs MVC controllers as the generated API shape.
- Blazor Server vs WASM vs Razor Pages as the generated UI shape —
  affects real-time/offline needs, hosting cost, and how much JS
  interop the generator ever needs to emit.
- How OU-based scope (`ORG_CELL_CONTEXT.md`) gets enforced in generated
  code — a base query filter is easy; column-level or report-vs-raw-data
  separation (parent sees aggregates, not records) is not, and needs a
  concrete design before it's assumed solvable.

## Status

Design only, not started. No code, no repo scaffolding, no chosen
templating library yet. Next step is picking one narrow vertical slice
(one entity, one relationship, one form) and generating it end-to-end
by hand first, to validate the regen/merge strategy before building a
generator around it.
