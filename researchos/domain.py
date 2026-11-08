"""Executable synthetic domain adapter, not independent scientific reproduction."""
from network_topology import analyze
DATA={'schema_version': 1, 'nodes': ['a', 'b', 'c'], 'edges': [['a', 'b'], ['b', 'a'], ['a', 'c'], ['c', 'a'], ['b', 'c'], ['c', 'b']], 'initial': {'a': 3, 'b': 1, 'c': 2}, 'failure_budget': 1}

def check():
    result=analyze(DATA)
    return {'domain':result['domain'],'statement':'The supplied synthetic synchronous network failure analysis fixture satisfies its declared reference checks.','passed':bool(not result["agreement_failures"]),
            'configuration':DATA,'observed':result,'scope':'Directed synchronous min-flooding for at most 12 nodes and 32 edges. Reliable links deliver messages every round. Enumerate baseline and optionally every single pre-start node/edge outage; simulate n-1 rounds and compare to an independent reachability oracle. No asynchronous consensus theorem, runtime crash recovery, Byzantine faults or deployment.'}
