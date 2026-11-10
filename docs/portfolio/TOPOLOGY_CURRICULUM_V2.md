# Topology compatibility and curriculum v2 — -Topology-for-Networks-and-Distributed-Systems

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | specialized graph tool |
| Minimum useful mathematics | Directed graph reachability; combinatorial topology only when an invariant is needed |
| Relationships to preserve | Directed links, synchronous rounds and pre-start outages |
| Concrete operation / capstone | Remove one directed edge and compare min-flooding against the reachability oracle |
| Necessity and scope boundary | Do not promote bounded synchronous failure enumeration into asynchronous or Byzantine consensus |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with directed graph reachability and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify directed links, synchronous rounds and pre-start outages. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain directed graph reachability; combinatorial topology only when an invariant is needed. | Remove one directed edge and compare min-flooding against the reachability oracle. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `ea93848bc48fa36512fb9fa6e3aed0c2d47295ff` in [network_topology/analysis.py](../../network_topology/analysis.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [1](../../network_topology/analysis.py#L1) | `"""Bounded synchronous min-flooding with static node/edge failure scenarios."""` | Explain the stated scope and identify a claim the implementation does not establish. |
| [3](../../network_topology/analysis.py#L3) | `def reachable(start,nodes,edges):` | State the input/output contract and trace one normal and one failing case. |
| [4](../../network_topology/analysis.py#L4) | `found={start};pending=[start]` | Trace discovery order and state the reachability or shortest-path invariant. |
| [5](../../network_topology/analysis.py#L5) | `while pending:` | Trace discovery order and state the reachability or shortest-path invariant. |
| [6](../../network_topology/analysis.py#L6) | `node=pending.pop()` | Trace discovery order and state the reachability or shortest-path invariant. |
| [7](../../network_topology/analysis.py#L7) | `for a,b in edges:` | Draw the represented relation; identify direction, multiplicity and edge labels. |
| [8](../../network_topology/analysis.py#L8) | `if a==node and b not in found:found.add(b);pending.append(b)` | Trace discovery order and state the reachability or shortest-path invariant. |
| [9](../../network_topology/analysis.py#L9) | `return found` | Predict the returned value and distinguish a computed result from authorization. |
| [12](../../network_topology/analysis.py#L12) | `def analyze(data):` | State the input/output contract and trace one normal and one failing case. |
| [13](../../network_topology/analysis.py#L13) | `if not isinstance(data,dict) or set(data)!={'schema_version','nodes','edges','initial','failure_budget'} or type(data['schema_version']) is not int or data['schema_version']!=1:raise ValueError('exact network schema_version 1 required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [14](../../network_topology/analysis.py#L14) | `nodes,edges,initial=data['nodes'],data['edges'],data['initial']` | Draw the represented relation; identify direction, multiplicity and edge labels. |
| [15](../../network_topology/analysis.py#L15) | `if not isinstance(nodes,list) or not 1<=len(nodes)<=12 or any(not isinstance(n,str) or not n or len(n)>32 for n in nodes) or len(set(nodes))!=len(nodes):raise ValueError('1..12 unique node IDs required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [16](../../network_topology/analysis.py#L16) | `if not isinstance(edges,list) or len(edges)>32 or any(not isinstance(e,list) or len(e)!=2 or any(n not in nodes for n in e) or e[0]==e[1] for e in edges):raise ValueError('at most 32 directed non-self edges required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [17](../../network_topology/analysis.py#L17) | `if len({tuple(e) for e in edges})!=len(edges):raise ValueError('duplicate edge')` | Construct the triggering input and explain why rejection preserves the contract. |
| [18](../../network_topology/analysis.py#L18) | `if not isinstance(initial,dict) or set(initial)!=set(nodes) or any(type(v) is not int or abs(v)>1000000 for v in initial.values()):raise ValueError('bounded integer initial values for every node required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [19](../../network_topology/analysis.py#L19) | `if type(data['failure_budget']) is not int or data['failure_budget'] not in (0,1):raise ValueError('failure_budget must be 0 or 1')` | Construct the triggering input and explain why rejection preserves the contract. |
| [20](../../network_topology/analysis.py#L20) | `nodes=sorted(nodes);edges=sorted(tuple(e) for e in edges)` | Draw the represented relation; identify direction, multiplicity and edge labels. |
| [21](../../network_topology/analysis.py#L21) | `scenarios=[('baseline',None,None)]` | Explain the statement, track its state change and predict its effect on the worked example. |
| [22](../../network_topology/analysis.py#L22) | `if data['failure_budget']:` | Trace both branches and identify the condition that changes the result. |
| [23](../../network_topology/analysis.py#L23) | `scenarios += [('node:'+n,n,None) for n in nodes]` | State the loop invariant, termination argument and one boundary case. |
| [24](../../network_topology/analysis.py#L24) | `scenarios += [('edge:'+a+'->'+b,None,(a,b)) for a,b in edges]` | Draw the represented relation; identify direction, multiplicity and edge labels. |
| [25](../../network_topology/analysis.py#L25) | `results=[]` | Explain the statement, track its state change and predict its effect on the worked example. |
| [26](../../network_topology/analysis.py#L26) | `for label,removed_node,removed_edge in scenarios:` | State the loop invariant, termination argument and one boundary case. |
| [27](../../network_topology/analysis.py#L27) | `active=[n for n in nodes if n!=removed_node]` | State the loop invariant, termination argument and one boundary case. |
| [28](../../network_topology/analysis.py#L28) | `links=[e for e in edges if removed_node not in e and e!=removed_edge]` | Draw the represented relation; identify direction, multiplicity and edge labels. |
| [29](../../network_topology/analysis.py#L29) | `values={n:initial[n] for n in active};history=[dict(values)];messages=0` | State the loop invariant, termination argument and one boundary case. |
| [30](../../network_topology/analysis.py#L30) | `for _ in range(max(0,len(active)-1)):` | State the loop invariant, termination argument and one boundary case. |
| [31](../../network_topology/analysis.py#L31) | `next_values=dict(values)` | Explain the statement, track its state change and predict its effect on the worked example. |
| [32](../../network_topology/analysis.py#L32) | `for a,b in links:next_values[b]=min(next_values[b],values[a]);messages+=1` | State the loop invariant, termination argument and one boundary case. |
| [33](../../network_topology/analysis.py#L33) | `values=next_values;history.append(dict(values))` | Explain the statement, track its state change and predict its effect on the worked example. |
| [34](../../network_topology/analysis.py#L34) | `expected={n:min(initial[s] for s in active if n in reachable(s,active,links)) for n in active}` | Trace discovery order and state the reachability or shortest-path invariant. |
| [35](../../network_topology/analysis.py#L35) | `if values!=expected:raise ValueError('independent reachability oracle mismatch')` | Construct the triggering input and explain why rejection preserves the contract. |
| [36](../../network_topology/analysis.py#L36) | `agreement=bool(active) and len(set(values.values()))==1` | Explain the statement, track its state change and predict its effect on the worked example. |
| [37](../../network_topology/analysis.py#L37) | `results.append({'scenario':label,'active_nodes':active,'final':values,'oracle':expected,'agreement':agreement,` | Explain the statement, track its state change and predict its effect on the worked example. |
| [38](../../network_topology/analysis.py#L38) | `'not_applicable':not active,'rounds':max(0,len(active)-1),'messages':messages,'history':history,` | Explain the statement, track its state change and predict its effect on the worked example. |
| [39](../../network_topology/analysis.py#L39) | `'strongly_connected':bool(active) and all(len(reachable(n,active,links))==len(active) for n in active)})` | Trace discovery order and state the reachability or shortest-path invariant. |
| [40](../../network_topology/analysis.py#L40) | `failures=[r['scenario'] for r in results if not r['agreement'] and not r['not_applicable']]` | State the loop invariant, termination argument and one boundary case. |
| [41](../../network_topology/analysis.py#L41) | `return {'schema_version':1,'domain':'networks','status':'FAIL' if failures else 'PASS','scenarios':results,'agreement_failures':failures,` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [42](../../network_topology/analysis.py#L42) | `'execution_authorized':False,` | Explain the statement, track its state change and predict its effect on the worked example. |
| [43](../../network_topology/analysis.py#L43) | `'scope':'Synchronous reliable directed links; only one static pre-start node or edge outage at a time. Min of reachable initial values after n-1 rounds. No asynchronous, Byzantine, delay, crash-during-run, deployment or general consensus-solvability claim.'}` | Trace discovery order and state the reachability or shortest-path invariant. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_domain.py](../../tests/test_domain.py)
- [tests/test_researchos.py](../../tests/test_researchos.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. Do not promote bounded synchronous failure enumeration into asynchronous or Byzantine consensus.
