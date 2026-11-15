# Synchronous network failure analysis

<!-- research-workbench:start -->
## Research workbench

[Open this repository's private workbench](https://tltmgnt-topology-for-networks-and-distributed-systems.troturn31.chatgpt.site) · [All repository workbenches](https://tltmgnt-research-workbenches.troturn31.chatgpt.site)

The hosted interface requires ChatGPT sign-in and access to the private Site. It supports browser-local research records, evidence fingerprints and workspace export. It is a prototype: no live AI model or repository backend is connected, and it does not establish external validation.
<!-- research-workbench:end -->


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

## Portfolio implementation boundary

See [current implementation and shared-core integration](docs/portfolio/INTEGRATION.md) and [machine-readable status](docs/portfolio/STATUS.json). Independent empirical reproduction and real-provider acceptance remain separate from software checks.

**∞**

## Topology compatibility and curriculum

See the [repository-specific v2 curriculum](docs/portfolio/TOPOLOGY_CURRICULUM_V2.md) for topology choices, worked explanations, a graded laboratory and adoption boundaries. Run the offline answer key from this repository root:\n\n```sh\npython curriculum/lab.py --verify\n```\n\n[Expected answers](curriculum/expected.json) · [Recorded local validation](curriculum/VALIDATION.json). The guide states any existing dependency needed for the lab.

# Topology for Networks and Distributed Systems

**NetTop** is a dependency-free Python toolkit for understanding undirected network structure, partition vulnerability, clique-complex topology, and an explicit synchronous averaging model. It connects graph structure to concrete failure scenarios without claiming to implement a production distributed protocol.

## Quick start

Requires Python 3.10 or newer. From the repository root:

```bash
python -m nettop examples/partition.json --output output/report.json --dot output/network.dot
python -m nettop examples/ring.json --rounds 200
```

The CLI prints JSON and optionally writes a report and Graphviz DOT file. Parent directories are created and existing output files are replaced. DOT can be rendered with a separately installed Graphviz viewer. No renderer is needed to analyze a graph.

Install the package to use the `nettop` command:

```bash
python -m pip install .
nettop --help
```

## JSON input

```json
{
  "nodes": ["a", "b", "c"],
  "edges": [["a", "b"], ["b", "c"]],
  "values": {"a": 0, "b": 3, "c": 6},
  "failures": {"nodes": ["b"], "edges": []}
}
```

Only `nodes` and `edges` are required. Nodes must be unique nonempty strings. Edges are undirected, unweighted node pairs. Self edges, duplicate/reversed edges, and unknown identifiers are rejected. An empty network is valid and is reported as not connected. The limit is 300 nodes; dense graphs can be expensive.

Optional `values` must give a finite numeric value for exactly every original node. Optional `failures` lists nodes and/or existing edges to remove simultaneously. A failed edge incident to a failed node is allowed. Failure reports retain the original membership size when calculating a majority.

## Python API

```python
from nettop import Network

network = Network(["a", "b", "c"], [["a", "b"], ["b", "c"]])
print(network.summary())
print(network.distances("a"))
print(network.failure_report(nodes=["b"]))
print(network.average({"a": 0, "b": 3, "c": 6}, rounds=100))
partitioned = network.without(nodes=["b"])
print(partitioned.components())
```

## Structural analysis

| Output | Meaning |
| --- | --- |
| Components and degrees | Reachable groups and neighbor counts |
| Diameter | Largest shortest-path distance, or `null` if disconnected/empty |
| Mean shortest path | Average distance over unordered distinct node pairs; `null` if disconnected/empty |
| Bridges | Edges whose removal increases the component count |
| Articulation nodes | Nodes whose removal increases the component count |
| Graph cycle rank | E − V + C: number of independent graph cycles |
| Clique-complex Betti 0 | Number of connected components |
| Clique-complex Betti 1 | Independent cycles remaining after filling triangle boundaries, over GF(2) |
| Triangle boundary rank | GF(2) rank computed by binary elimination, accounting for dependent boundaries |

For a singleton, diameter and mean shortest path are zero. Low-link traversal finds cuts across all components. Betti 1 uses the clique (flag) complex: every clique is a simplex, so a triangle is filled and has Betti 1 = 0, while an unchorded four-node ring has Betti 1 = 1. Higher simplices do not change this H1 calculation. The toolkit computes no higher Betti numbers.

A clique-complex cycle is not automatically a physical coverage hole. Inferring geographic sensor coverage requires a justified geometric/coverage model and additional assumptions; arbitrary communication edges do not supply that information. Graph connectivity also does not capture protocol-state topology or distributed-computing impossibility results.

## Failure and quorum model

`failure_report` removes specified nodes and edges, lists the surviving components, and finds those with at least `floor(N/2) + 1` members, where N is the **original** membership. This is a static majority-capacity check under undirected reachability. It does not establish election success, safe replication, timely responses, or protocol liveness. Removing failed members does not silently lower the threshold.

In `examples/partition.json`, five nodes initially connect through the bridge c–d. Removing it creates components {a,b,c} and {d,e}. The majority threshold stays three, so only {a,b,c} has enough surviving members. This assumes all listed members are eligible voters; weights, learners, membership changes, and joint quorums are outside the model.

## Averaging model

The simulator runs simultaneous rounds on a static graph using

`x_i(next) = (1 − α degree(i)) x_i + α Σ x_j`, with `α = 1 / (maximum degree + 1)`.

This lazy, symmetric update preserves each component's arithmetic mean and converges within connected components. It assumes reliable instantaneous neighbor exchange, synchronous rounds, no malicious participants, and no changing topology during a run. It is an illustrative numerical model, not Raft, Paxos, Byzantine agreement, or a networked service.

`converged` means the maximum absolute error from the initial component means is at most `--tolerance` (default 1e-6). `global_agreement` means the final numerical range is within that tolerance; disconnected components can happen to agree if their means match. Empty output agrees vacuously. Zero rounds returns the initial values. The simulator always executes the requested number of rounds, up to 10,000.

The CLI reports two **independent** runs: `averaging` on the original topology and `post_failure_averaging` on the surviving topology, restarted from surviving nodes' original values. It does not remove nodes midway through the first run. In the partition example, surviving component means are 2 and 12, so component convergence does not produce global agreement.

## Scope and verification

Supports small, static, undirected, unweighted graphs. It does not discover live networks, send messages, inject real failures, model bandwidth/latency, analyze directed reachability, simulate packet loss, or certify operational availability. Numerical averaging is subject to floating-point precision. Very large numeric ranges may be rejected.

```bash
python -m unittest discover -s tests -v
```

The 15 tests cover known graph distances, cut detection against node/edge removal on **all 64 simple four-node graphs**, clique homology with dependent triangle boundaries, mean preservation, disconnected averaging, fixed-membership quorum behavior, invalid input, CLI reports, and DOT escaping. CI installs the package and runs the tests and examples on Python 3.10, 3.12, and 3.13.

Licensed under Apache 2.0; see [LICENSE](LICENSE).

## ResearchOS / TECT assurance layer

This repository includes the shared v0.1 research controller, a scoped executable domain pilot, replayable evidence/decision bundles, adversarial regression probes, and explicit unassured outcomes. See [the workflow](docs/RESEARCHOS.md), [versioned semantics](docs/TECT_SPEC.md), and [research-program traceability](docs/TECT_RESEARCH_PLAN.md). Existing domain results retain their documented limits. No claim state authorizes external or clinical execution.
