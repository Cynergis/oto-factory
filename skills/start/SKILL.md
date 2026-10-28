---
name: start
description: >-
  Start with the OTO factory: build a component of a product from the spec its OTO architecture graph
  projects, with a runner that stays inside the component's write scope and an evaluator that passes
  judgement on the criteria the graph drew. Use when someone wants to build, implement or generate a
  component from an OTO graph, run the factory, or asks what the factory needs before it can build.
---

# OTO Factory

Build a component from what the graph says about it, and nothing else. The factory is a use case of
the OTO knowledge graph in its own repository (Cynergis/oto-factory, ADR-0007 of the engine): this
pack brings the `factory-run` ontology, the `oto factory` commands in its own code, the runner,
evaluator and aggregator agents, the hooks that keep a run inside its scope, and the spec-context
skill the runner loads before it edits.

## Talking with the person

- **Plain, natural language, in the person's words.** Say what the factory will build and from what;
  never paste what a command printed unless the person asks.
- **Technical details only when the person asks for them.**
- **The same clear shape every time:** say what we are about to do, check what the graph has, read
  back what you understood, confirm, then say what is next.

1. **What a build needs.** An OTO project with the `architecture` ontology (or `ddd` over it) whose
   graph holds the component to build: its context, use cases, the contracts it exposes and consumes,
   its requirements with budgets, its decisions and controls. `oto status --project <graph>` says
   what the graph has; a component that the spec cannot project is not ready to build, and the
   person should curate it first (the engine's skills: capture-form, curate).

2. **The spec and the scope.** From the code repository:

   ```bash
   oto factory spec component.<id> --out .factory/spec.json --project <graph>
   oto factory scope component.<id> --cap 5 --allow <paths> --out .factory/run.json --project <graph>
   oto factory criteria --component component.<id> --out .factory/criteria --project <graph>
   ```

   The spec is hashed over its own content; `oto factory spec --check .factory/spec.json` refuses a
   hand edit. The scope is what the runner may write; the criteria are what the evaluator judges by.

3. **The run.** Hand the component to the **runner** agent (it loads `spec-context`, edits inside the
   scope, stops when the criteria pass or the iteration cap is reached), then to the **evaluator**
   (no edit tools; writes `.factory/verdict.json`). Several components: `oto factory plan --all` gives
   the build order from contract dependencies, and the **aggregator** sums the verdicts. In CI, the
   workflow `workflows/oto-factory.yml` runs the same plugin with the same hooks.

4. **What comes back to the graph.** `oto factory run sync --events .factory/events.jsonl` reads the
   run into its own graph; `oto factory run metrics` queries it; `oto work event verdict` (the work
   pack) blocks the work item on a named person when a build fails or escalates; `oto factory
   deviate` records what the runner found impossible as specified, as a change proposal with the
   evidence.

## What the ontology declares

The `factory-run` ontology: a Run of a plan over components, each Iteration with what the runner
touched and what the hooks refused, the Verdict (pass, fail, escalated) with its gaps, and the
metrics that are queries over them. The README of the pack describes each command and the run graph.
