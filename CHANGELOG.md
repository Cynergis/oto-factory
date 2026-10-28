# Changelog

What each release of the factory changed. The engine's own changelog is in Cynergis/oto.

## 4.0.0 — 2026-10-28

**Its own repository.** The plugin version is the pack release from now on, as for every OTO pack (0.3.0 → 4.0.0). The factory is a use case of the OTO graph, not a knowledge graph
([ADR-0007](https://github.com/Cynergis/oto/blob/main/docs/adr/0007-a-use-case-lives-outside-the-engine.md)
in the engine), so it leaves the engine's repository whole: the plugin (agents, hooks, the
spec-context skill, the Actions workflow), the factory-run ontology at release 3 carrying the
engine-side commands in its `code/` (the spec projection, the plan, the scope, the run graph,
criteria, deviations, metrics and `oto factory`), the tests and the E2E. The engine loads the
commands from the pack when it is installed; nothing of the factory ships with the engine any more.
Needs an engine that loads a pack's `code/`: built from main after 2026-10-28, or 0.14.2 and later.

Earlier releases, 0.1.0 to 0.3.0, shipped inside the engine's repository; their notes are in the
README's Releases section.
