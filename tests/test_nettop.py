import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from nettop import Network


def graph(n,edges):
    return Network([str(i) for i in range(n)],[[str(a),str(b)] for a,b in edges])


class ConnectivityTests(unittest.TestCase):
    def test_path(self):
        network=graph(4,[(0,1),(1,2),(2,3)])
        report=network.summary()
        self.assertEqual(report['diameter'],3)
        self.assertAlmostEqual(report['mean_shortest_path'],10/6)
        self.assertEqual(report['articulation_nodes'],['1','2'])
        self.assertEqual(len(report['bridges']),3)

    def test_cuts_against_removal_oracle(self):
        # Every simple graph on four nodes, including disconnected cases.
        edges=list(itertools.combinations(range(4),2))
        for mask in range(1<<len(edges)):
            network=graph(4,[e for i,e in enumerate(edges) if mask&(1<<i)])
            before=len(network.components()); result=network.cuts()
            expected_nodes=[n for n in network.nodes if len(network.without([n]).components())>before]
            expected_edges=[list(e) for e in network.edges if len(network.without(edges=[e]).components())>before]
            self.assertEqual(result['articulation_nodes'],expected_nodes)
            self.assertEqual(result['bridges'],expected_edges)

    def test_empty_singleton_disconnected(self):
        self.assertEqual(graph(0,[]).topology()['betti_0'],0)
        self.assertFalse(graph(0,[]).summary()['connected'])
        self.assertEqual(graph(1,[]).summary()['diameter'],0)
        self.assertIsNone(graph(2,[]).summary()['diameter'])
        self.assertIsNone(graph(2,[]).summary()['mean_shortest_path'])

    def test_invalid_networks(self):
        for nodes,edges in [(['a','a'],[]),(['a'],[['a','a']]),(['a'],[['a','b']]),(['a','b'],[['a','b'],['b','a']]),([1],[])]:
            with self.assertRaises(ValueError): Network(nodes,edges)
        with self.assertRaises(ValueError): graph(2,[]).without(['missing'])
        with self.assertRaises(ValueError): graph(2,[]).without(edges=[['0','1']])


class TopologyTests(unittest.TestCase):
    def test_unfilled_ring(self):
        t=graph(4,[(0,1),(1,2),(2,3),(3,0)]).topology()
        self.assertEqual((t['betti_0'],t['betti_1'],t['graph_cycle_rank']),(1,1,1))

    def test_triangle_is_filled(self):
        t=graph(3,[(0,1),(1,2),(2,0)]).topology()
        self.assertEqual((t['graph_cycle_rank'],t['triangle_count'],t['betti_1']),(1,1,0))

    def test_dependent_triangle_boundaries(self):
        t=graph(4,list(itertools.combinations(range(4),2))).topology()
        self.assertEqual(t['triangle_count'],4)
        self.assertEqual(t['triangle_boundary_rank'],3)
        self.assertEqual(t['betti_1'],0)

    def test_disconnected_cycles(self):
        t=graph(7,[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,4)]).topology()
        self.assertEqual((t['betti_0'],t['betti_1']),(2,1))


class DistributedModelTests(unittest.TestCase):
    def test_average_preserves_mean(self):
        network=graph(4,[(0,1),(1,2),(2,3)])
        result=network.average({'0':0,'1':2,'2':4,'3':10},200)
        self.assertTrue(result['converged'])
        self.assertTrue(result['global_agreement'])
        self.assertAlmostEqual(sum(result['values'].values()),16)
        for value in result['values'].values(): self.assertAlmostEqual(value,4)

    def test_partition_component_means(self):
        network=graph(4,[(0,1),(2,3)])
        result=network.average({'0':0,'1':2,'2':10,'3':14},10)
        self.assertEqual(result['values'],{'0':1,'1':1,'2':12,'3':12})
        self.assertTrue(result['converged']); self.assertFalse(result['global_agreement'])

    def test_majority_uses_original_membership(self):
        network=graph(5,[(0,1),(1,2),(2,3),(3,4)])
        report=network.failure_report(edges=[['2','3']])
        self.assertEqual(report['majority_threshold'],3)
        self.assertEqual(report['majority_capable_components'],[['0','1','2']])
        report=network.failure_report(nodes=['2','3','4'])
        self.assertEqual(report['majority_capable_components'],[])
        self.assertEqual(network.failure_report(nodes=list(network.nodes))['surviving_nodes'],0)

    def test_zero_rounds_and_validation(self):
        network=graph(2,[(0,1)])
        result=network.average({'0':0,'1':2},0)
        self.assertFalse(result['converged']); self.assertEqual(result['values'],{'0':0,'1':2})
        for values in [{},{'0':0,'1':float('nan')},{'0':0,'1':True}]:
            with self.assertRaises(ValueError): network.average(values)
        with self.assertRaises(ValueError): network.average({'0':0,'1':2},-1)


class CliTests(unittest.TestCase):
    def test_exports_and_failure_model(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'report.json'; dot=Path(d)/'graph.dot'
            proc=subprocess.run([sys.executable,'-m','nettop','examples/partition.json','--output',str(target),'--dot',str(dot)],capture_output=True,text=True,check=True)
            report=json.loads(proc.stdout)
            self.assertEqual(report,json.loads(target.read_text()))
            self.assertEqual(report['failure_analysis']['majority_capable_components'],[['a','b','c']])
            self.assertFalse(report['post_failure_averaging']['global_agreement'])
            self.assertIn('"a" -- "b";',dot.read_text())

    def test_dot_escaping(self):
        self.assertIn('"a\\\"b";',Network(['a"b'],[]).dot())

    def test_invalid_cli(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'invalid.json'; path.write_text('{"nodes":["a"],"edges":[["a","x"]]}')
            proc=subprocess.run([sys.executable,'-m','nettop',str(path)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2); self.assertNotIn('Traceback',proc.stderr)


if __name__=='__main__': unittest.main()
