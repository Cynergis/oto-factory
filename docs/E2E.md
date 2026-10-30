# Testing the factory end to end

The factory's own E2E, moved from the engine's `docs/E2E-TESTING.md` (section 22, the phase 5 part)
when the factory left the engine's repository (ADR-0007). `oto` is the engine, installed with this
pack: the engine finds the `factory-run` ontology and its code under this repository's `ontology/`
when the plugin is installed, or with `OTO_ONTOLOGIES=<this repository>/ontology` from a checkout.
The projects named here (`domain`, the invoice model) are the engine's `ddd` and `architecture` samples.

Then the factory's inputs, read from the graph (I3 to I5):

```bash
oto query --project domain ask AR10 NODE=component.approval-policy            # the contracts it consumes, frozen
oto factory spec component.invoice-intake --out specs/invoice-intake.spec.json --project domain
oto factory spec --check specs/invoice-intake.spec.json --project domain       # holds; edit the file by hand and it is refused
oto factory plan --all --project domain                                         # 3 build(s) in 1 group(s): the contracts are frozen
oto decide contract.invoice-events-v1 status=draft --by "Sam Lee" --at 2026-10-27 --project domain
oto factory plan --all --project domain                                         # 2 groups: the policy waits for the intake
oto factory plan --project domain                                               # the components of the contexts a person signed off
```

Pass when AR10 lists the policy's two frozen contracts; the spec carries the context, the use case,
the exposed interfaces with their contracts, REQ-042 with its budget and measurement, the PII
control on the JDBC connection, the connections, the module with its last commit, and a hash that
`--check` holds and that a hand edit breaks; the plan is three parallel builds while every contract
is frozen, two groups once one is a draft, nothing while no context is signed off (said with the
command that signs one off), the signed-off context's component once one is, and a cycle of draft
dependencies is named rather than looped.

Then the factory plugin on files (J1, J2, J7 first cut), in the code repository:

```bash
oto factory spec component.invoice-intake --out /path/to/invoice-platform/.factory/spec.json --project domain
oto factory scope component.invoice-intake --cap 3 --allow tests/intake --out /path/to/invoice-platform/.factory/run.json --project domain
cd /path/to/invoice-platform
echo '{"tool_name": "Edit", "tool_input": {"file_path": "src/scheduler/main.py"}, "cwd": "'$PWD'"}' | python3 -I /path/to/oto-factory/hooks/guard.py; echo "exit $?"      # 2: outside the scope
echo '{"tool_name": "Write", "tool_input": {"file_path": "contracts/x.json"}, "cwd": "'$PWD'"}' | python3 -I /path/to/oto-factory/hooks/guard.py; echo "exit $?"      # 2: read-only
echo '{"tool_name": "Edit", "tool_input": {"file_path": "src/intake/app.py"}, "cwd": "'$PWD'"}' | python3 -I /path/to/oto-factory/hooks/guard.py; echo "exit $?"      # 0
echo '{"cwd": "'$PWD'", "stop_hook_active": false}' | python3 -I /path/to/oto-factory/hooks/loop.py                                                             # block: no verdict yet
echo '{"verdict": "fail", "gaps": ["the IBAN is not validated"]}' > .factory/verdict.json
echo '{"cwd": "'$PWD'", "stop_hook_active": true}' | python3 -I /path/to/oto-factory/hooks/loop.py                                                              # block: the gap
# twice more: the cap of 3 is reached, the run is escalated
/plugin marketplace add Cynergis/oto && /plugin install oto@cynergis-engine && /plugin marketplace add Cynergis/oto-registry && /plugin install oto-factory@cynergis                                                                           # in Claude Code
```

Pass when the scope names the component's modules and what `--allow` adds, `contracts/` read-only,
the cap and the spec's hash; the guard refuses an edit outside the scope or into `contracts/`, and
a shell command that writes a contract, allows reads and edits inside the scope, does nothing with
no run and blocks every write with a broken snapshot; the loop sends the runner to the evaluator
without a verdict, back to the gaps on a fail, ends on a pass, and at the cap lets the session stop
with the run escalated; the agents' definitions give the evaluator no edit tool and say it never
sees the runner's reasoning; and the registry's marketplace lists `oto-factory` beside `oto`.

Then the run graph and promotion (I8, J4, M4):

```bash
oto factory plan --all --json --out plan.json --project domain
oto factory run start --plan plan.json --at 2026-10-27 --id r-001 --runs .factory/runs          # one OTO project per run
oto factory run status --run .factory/runs/r-001                                                 # 3 builds, planned
# the loop hook appends its decisions to .factory/events.jsonl in the code repository (run.json names the run: "run": "r-001")
oto factory run sync --run .factory/runs/r-001 --events /path/to/invoice-platform/.factory/events.jsonl
oto factory run record --run .factory/runs/r-001 --component component.invoice-intake --iteration 2 --verdict pass --at 2026-10-27T11:00:00Z
oto factory run replay --run .factory/runs/r-001 --component component.invoice-intake
oto build --project .factory/runs/r-001 && oto query --project .factory/runs/r-001 ask FR1 RUN=run.r-001
oto factory run promote --run .factory/runs/r-001 --component component.invoice-intake --commit <sha> --at 2026-10-28 --into domain
oto curate start --project domain && oto curate add --from proposals/run-r-001-invoice-intake.json --project domain && oto curate check --project domain && oto curate apply --by "<you>" --note "promoted from run r-001" --project domain
oto work event verdict --item workitem.e-checkout --run r-001 --component component.payment-scheduler --verdict escalated --gap "cap reached" --waiting-on person.m-okafor --at 2026-10-28 --project plan
```

Pass when the run project holds the Run with its plan instance and a planned Build per component,
its audit log names the engine, and starting the same id again is refused; `sync` reads each event
once (a second sync adds nothing) and the builds read passed or escalated with their iterations; an
iteration is recorded once and `replay` lists them in order with their gaps; FR1 to FR3 answer;
`promote` refuses a build that has not passed, and for one that has writes the run document and a
proposal with the evidence, the commit touching the component's modules and no run state, which
the gates take and AR5 then shows; and a failed or escalated verdict blocks the work item on the
named person with the gaps as the reason while a pass is noted and changes no state.

Then the criteria, a deviation and a measurement (I6, I7, H5, H6):

```bash
oto factory criteria --context bc.checkout --out criteria/checkout --project domain          # criteria.md, criteria.json, test_criteria_checkout.py
oto factory criteria --component component.invoice-intake --out criteria/intake --project domain   # its context's scenarios and rules, its budget, its control
oto factory deviate --run .factory/runs/r-001 --component component.approval-policy --about contract.invoice-events-v1 \
  --observed "InvoiceSubmitted carries no supplier id, which the approval rules need" --proposes "Add supplier_id as version 2 of the invoice events contract" \
  --at 2026-10-28 --into domain                                                                 # the siblings through the contract, the build failed
oto curate start --project domain && oto curate add --from proposals/deviation-r-001-1.json --project domain && oto curate check --project domain && oto curate apply --by "<you>" --note "a deviation" --project domain
oto query --project domain ask AR7                                                              # the proposal, prompted by what was observed
oto arch measure --nfr nfr.req-042 --from k6-summary.json --at 2026-10-29 --source https://ci.invoice.example/runs/2026-10-29/k6 --project domain
oto curate start --project domain && oto curate add --from proposals/measure-req-042-2026-10-29.json --project domain && oto curate check --project domain && oto curate apply --by "<you>" --note "the k6 run" --project domain
oto build --project domain && oto query --project domain ask AR6 NFR=nfr.req-042                # p95 870 ms over 5000 requests
```

Pass when the criteria name every scenario (given, when, then), rule, policy, budget and control
with the nodes they came from, the skeleton compiles with one skipped test per criterion, a
component no context runs as is refused with the way out; the deviation's document, evidence and
change proposal cite each other, the siblings are the components that consume or expose the
contract and never the deviating one, the run's build reads failed, and AR7 lists the proposal
after the gates; and a JUnit, a coverage.py and a k6 report each read as one value, the
measurement goes through the gates, and AR6 and `arch_context` show it next to the budget.

**The last cut of phase 5: the spec-context skill, the Actions path, metrics, the release.** The
runner starts from the graph, both execution environments run the same hooks, and the metrics are
queries over the run graph.

```bash
# the runner's first move, locally in Claude Code with the oto-factory plugin: load the spec-context skill, then
oto factory spec component.invoice-intake --out .factory/spec.json --project domain
oto factory spec --check .factory/spec.json --project domain                                    # the hash in run.json must agree
oto factory criteria --component component.invoice-intake --out .factory/criteria --project domain
oto query --project domain ask DD22 CONTEXT=bc.invoice-approval                                 # what the builder must produce
oto query --project domain ask AR10 NODE=component.invoice-intake                               # the contracts it consumes, frozen or draft
# in CI: copy workflows/oto-factory.yml to .github/workflows/ of the code repository, set ANTHROPIC_API_KEY,
# run it with component=component.invoice-intake; the same plugin, so the same guard and loop hooks; the run graph is the artifact
# the evaluator writes what the tests said beside its verdict: {"verdict": "fail", "gaps": [...], "tests": "pass"}
oto factory run record --run .factory/runs/r-001 --component component.invoice-intake --iteration 2 --verdict fail --tests pass \
  --gap "the IBAN is not validated" --at 2026-10-27T11:00:00Z                                  # by hand, where there is no hook
oto factory run metrics --run .factory/runs/r-001                                               # iterations to pass, escalation rate, disagreements, cost
oto factory run metrics --runs .factory/runs --json                                             # over every run
oto build --project .factory/runs/r-001 && oto query --project .factory/runs/r-001 ask FR4 RUN=run.r-001   # tests passed, the evaluator failed
# the release: .claude-plugin/plugin.json says the plugin's version and the registry's marketplace pins its tag; the README has a Releases section
# the roadmap: a phase is reached when a named person says so
oto decide milestone.phase-5 state=reached --by "Chiheb Dkhil" --at 2026-10-26 --project roadmap
oto build --project roadmap && oto audit verify --project roadmap
```

Pass when the skill parses, names only commands the engine has and the runner loads it first; the
workflow runs `anthropics/claude-code-action` with the `oto-factory` plugin, writes spec, scope and
criteria from the graph, syncs the events after the build and uploads the run graph; `--tests` is
kept on the iteration and the loop hook carries it from `verdict.json` into the events; the metrics
give the mean iterations to pass over the passed builds, the escalation rate over the ended ones,
the FR4 and FR5 disagreements by build, and say cost is not recorded; the two version numbers are
equal; and `milestone.phase-5` reads reached with the assertion among its sources, phase 6 still
planned, the audit chain intact.

