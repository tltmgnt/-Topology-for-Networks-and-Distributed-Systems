# Synchronous network failure analysis

Working offline Python research prototype. **Directed synchronous min-flooding for at most 12 nodes and 32 edges. Reliable links deliver messages every round. Enumerate baseline and optionally every single pre-start node/edge outage; simulate n-1 rounds and compare to an independent reachability oracle. No asynchronous consensus theorem, runtime crash recovery, Byzantine faults or deployment.**

## Run

Python 3.10+, standard-library runtime. No model account, paid service or external action.

```sh
python -m pip install .
mkdir -p runs
network-topology analyze examples/reference.json --output runs/reference
network-topology verify runs/reference
researchos pilot --output runs/pilot
# Expected exit 1: domain computation is captured; independent reproduction and domain attacks are missing.
researchos verify runs/pilot
python -m unittest discover -s tests -v
python tests/check_installed.py
python tests/check_researchos_installed.py
```

Each package has its own virtual environment: the vendored `researchos` command shares a name across repositories. Existing outputs are never overwritten. `analyze`: exit 0 scoped checks pass, 1 scoped requirements fail, 2 invalid input/I/O. `verify`: exit 0 means exact recomputation matches, including a correctly recorded failing result; exit 2 means invalid or changed bundle. Replay records Python version and requires the same numerical environment.

Input uses strict JSON, rejects duplicate keys and nonfinite values, limits size to 4 MiB and nesting to 32. See [reference input](examples/reference.json), source-level validation and [methods/limits](docs/METHODS.md). Review bundles contain input, report, escaped HTML and a hash manifest. Hashes and local replay establish consistency, not source authenticity or independent reproduction. Synthetic fixtures are software checks; a real independently adjudicated study remains outstanding.

## ResearchOS / TECT

A scoped executable domain adapter feeds the shared, versioned controller. The pilot remains unassured when evidence is missing. [Workflow](docs/RESEARCHOS.md), [semantics](docs/TECT_SPEC.md), [research plan](docs/TECT_RESEARCH_PLAN.md), and [concept paper](docs/researchos/TECT_WHITE_PAPER.md). The shared implementation is governed by the canonical ResearchOs release manifest; local copies are conformance-checked rather than independently evolved.

No report grants clinical, financial, equipment or deployment authority. Original Apache-2.0 license retained.
