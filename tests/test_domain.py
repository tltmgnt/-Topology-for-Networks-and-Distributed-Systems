import copy,itertools,tempfile,unittest
from pathlib import Path
from network_topology import analyze
from network_topology.io import create,verify

def model(nodes,edges,values=None,budget=0):return {'schema_version':1,'nodes':nodes,'edges':edges,'initial':values or {n:i for i,n in enumerate(nodes)},'failure_budget':budget}

class DomainTests(unittest.TestCase):
    def test_complete_survives_single_outage(self):
        nodes=list('abc');r=analyze(model(nodes,[list(e) for e in itertools.permutations(nodes,2)],budget=1));self.assertEqual(r['status'],'PASS');self.assertEqual(len(r['scenarios']),10)
    def test_directed_chain_not_agreement(self):
        r=analyze(model(list('abc'),[['a','b'],['b','c']],{'a':3,'b':2,'c':1}));self.assertEqual(r['status'],'FAIL');self.assertEqual(r['scenarios'][0]['final'],{'a':3,'b':2,'c':1})
    def test_chain_min_source(self):self.assertEqual(analyze(model(list('abc'),[['a','b'],['b','c']]))['status'],'PASS')
    def test_disconnected_same_values_not_strong_connectivity(self):
        r=analyze(model(list('ab'),[],{'a':1,'b':1}));self.assertEqual(r['status'],'PASS');self.assertFalse(r['scenarios'][0]['strongly_connected'])
    def test_star_center_failure(self):
        r=analyze(model(list('abc'),[['a','b'],['b','a'],['a','c'],['c','a']],budget=1));self.assertIn('node:a',r['agreement_failures'])
    def test_singleton_failure_not_applicable(self):
        r=analyze(model(['a'],[],budget=1));self.assertEqual(r['status'],'PASS');self.assertTrue(r['scenarios'][1]['not_applicable'])
    def test_all_64_directed_graphs(self):
        nodes=list('abc');edges=list(itertools.permutations(nodes,2))
        # With distinct source values, direct path expansion independently predicts final minima.
        for mask in range(64):
            links=[list(e) for i,e in enumerate(edges) if mask>>i&1]
            result=analyze(model(nodes,links))['scenarios'][0]
            paths={(n,n) for n in nodes}|{tuple(e) for e in links}
            for _ in range(3):paths|={(a,d) for a,b in list(paths) for c,d in list(paths) if b==c}
            expected={n:min(nodes.index(s) for s in nodes if (s,n) in paths) for n in nodes}
            self.assertEqual(result['final'],expected)
    def test_message_accounting(self):self.assertEqual(analyze(model(list('abc'),[['a','b'],['b','c']]))['scenarios'][0]['messages'],4)
    def test_duplicate_edge_rejected(self):
        with self.assertRaises(ValueError):analyze(model(list('ab'),[['a','b'],['a','b']]))
    def test_missing_endpoint_rejected(self):
        with self.assertRaises(ValueError):analyze(model(['a'],[['a','b']]))
    def test_bad_budget(self):
        with self.assertRaises(ValueError):analyze(model(['a'],[],budget=True))
    def test_replay(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a';create(p,model(list('ab'),[]));self.assertEqual(verify(p)['status'],'FAIL')
