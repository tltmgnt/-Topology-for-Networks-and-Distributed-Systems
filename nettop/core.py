"""Small undirected network analysis and explicit distributed-system models."""
from collections import deque
import json
import math


class Network:
    """Simple undirected unweighted graph with stable string node identifiers."""
    def __init__(self, nodes, edges):
        if not isinstance(nodes,list) or any(not isinstance(n,str) or not n for n in nodes):
            raise ValueError('nodes must be a list of nonempty strings')
        if len(set(nodes))!=len(nodes) or len(nodes)>300:
            raise ValueError('Node identifiers must be unique; at most 300 nodes')
        if not isinstance(edges,list): raise ValueError('edges must be a list')
        self.nodes=tuple(sorted(nodes))
        self.adjacency={n:set() for n in self.nodes}
        seen=set()
        for e in edges:
            if not isinstance(e,(list,tuple)) or len(e)!=2 or any(not isinstance(n,str) or n not in self.adjacency for n in e):
                raise ValueError('Each edge must name two existing nodes')
            a,b=sorted(e)
            if a==b or (a,b) in seen: raise ValueError('Self edges and duplicate edges are unsupported')
            seen.add((a,b)); self.adjacency[a].add(b); self.adjacency[b].add(a)
        self.edges=tuple(sorted(seen))

    def distances(self, source):
        if source not in self.adjacency: raise ValueError('Unknown source node')
        distance={source:0}; queue=deque([source])
        while queue:
            a=queue.popleft()
            for b in sorted(self.adjacency[a]):
                if b not in distance:
                    distance[b]=distance[a]+1; queue.append(b)
        return distance

    def components(self):
        remaining=set(self.nodes); result=[]
        while remaining:
            component=sorted(self.distances(min(remaining)))
            result.append(component); remaining.difference_update(component)
        return result

    def cuts(self):
        """Tarjan low-link algorithm for bridges and articulation vertices."""
        discovery,low,parent={},{},{}
        bridges,points=[],set()
        def visit(a):
            discovery[a]=low[a]=len(discovery)
            children=0
            for b in sorted(self.adjacency[a]):
                if b not in discovery:
                    parent[b]=a; children+=1; visit(b); low[a]=min(low[a],low[b])
                    if low[b]>discovery[a]: bridges.append([min(a,b),max(a,b)])
                    if a in parent and low[b]>=discovery[a]: points.add(a)
                elif parent.get(a)!=b: low[a]=min(low[a],discovery[b])
            if a not in parent and children>1: points.add(a)
        for n in self.nodes:
            if n not in discovery: visit(n)
        return {'bridges':sorted(bridges),'articulation_nodes':sorted(points)}

    def without(self, nodes=(), edges=()):
        removed=set(nodes)
        if not removed.issubset(self.adjacency): raise ValueError('Unknown failed node')
        failed=set()
        for edge in edges:
            if len(edge)!=2: raise ValueError('Failed edges require two nodes')
            e=tuple(sorted(edge))
            if e not in self.edges: raise ValueError('Unknown failed edge')
            failed.add(e)
        return Network([n for n in self.nodes if n not in removed],
                       [e for e in self.edges if not removed.intersection(e) and e not in failed])

    def topology(self):
        """Betti 0 and 1 of the flag/clique complex over GF(2).

        Triangle boundaries span im(d2); higher cliques do not affect H1.
        """
        indices={edge:i for i,edge in enumerate(self.edges)}
        pivots={}; triangles=0
        for a,b in self.edges:
            for c in sorted(self.adjacency[a]&self.adjacency[b]):
                if c<=b: continue
                triangles+=1
                boundary=(1<<indices[(a,b)]) ^ (1<<indices[(a,c)]) ^ (1<<indices[(b,c)])
                while boundary:
                    pivot=boundary.bit_length()-1
                    if pivot not in pivots:
                        pivots[pivot]=boundary; break
                    boundary ^= pivots[pivot]
        beta0=len(self.components())
        rank=len(self.edges)-len(self.nodes)+beta0
        return {'betti_0':beta0,'betti_1':rank-len(pivots),
                'graph_cycle_rank':rank,'triangle_count':triangles,
                'triangle_boundary_rank':len(pivots),'coefficient_field':'GF(2)',
                'complex':'clique complex'}

    def summary(self):
        components=self.components(); connected=len(components)==1
        distances=[self.distances(n) for n in self.nodes]
        total=sum(sum(d.values()) for d in distances)/2
        count=len(self.nodes)*(len(self.nodes)-1)/2
        return {'node_count':len(self.nodes),'edge_count':len(self.edges),
                'components':components,'connected':connected,
                'degrees':{n:len(self.adjacency[n]) for n in self.nodes},
                'diameter':max((max(d.values()) for d in distances),default=0) if connected else None,
                'mean_shortest_path':total/count if connected and count else (0 if connected else None),
                **self.cuts(),'topology':self.topology()}

    def failure_report(self, nodes=(), edges=()):
        """Static partition capacity for a fixed original membership majority."""
        surviving=self.without(nodes,edges)
        required=len(self.nodes)//2+1
        components=surviving.components()
        return {'original_membership':len(self.nodes),'majority_threshold':required,
                'surviving_nodes':len(surviving.nodes),'components':components,
                'majority_capable_components':[c for c in components if len(c)>=required],
                'largest_component_size':max(map(len,components),default=0),
                'model':'Fixed original membership; undirected reachability only, not protocol liveness'}

    def average(self, values, rounds=100, tolerance=1e-6):
        """Synchronous lazy Laplacian averaging with step 1/(max_degree+1).

        Each connected component preserves its own mean. No message loss/delay.
        """
        if not isinstance(values,dict) or set(values)!=set(self.nodes):
            raise ValueError('values must contain exactly every node')
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in values.values()):
            raise ValueError('Initial values must be finite numbers')
        if type(rounds) is not int or not 0<=rounds<=10000:
            raise ValueError('rounds must be an integer from 0 to 10000')
        if not math.isfinite(tolerance) or tolerance<=0:
            raise ValueError('tolerance must be positive and finite')
        components=self.components()
        targets={n:math.fsum(values[k]/len(c) for k in c) for c in components for n in c}
        current={n:float(values[n]) for n in self.nodes}
        alpha=1/(1+max(map(len,self.adjacency.values()),default=0))
        completed=0
        for _ in range(rounds):
            updated={}
            for n in self.nodes:
                # Convex combination avoids overflow from subtracting large values.
                updated[n]=math.fsum([current[n]*(1-alpha*len(self.adjacency[n]))]+
                                    [alpha*current[k] for k in sorted(self.adjacency[n])])
            current=updated; completed+=1
        error=max((abs(current[n]-targets[n]) for n in self.nodes),default=0)
        if not math.isfinite(error): raise ValueError('Numerical range exceeded')
        return {'rounds':completed,'values':current,'component_mean_targets':targets,
                'max_error_to_component_mean':error,'converged':error<=tolerance,
                'tolerance':tolerance,'global_agreement':max(current.values(),default=0)-min(current.values(),default=0)<=tolerance,
                'step_size':alpha,'model':'Synchronous static undirected averaging; not fault-tolerant consensus'}

    def dot(self):
        """Graphviz DOT with JSON-escaped identifiers; no Graphviz dependency."""
        quote=lambda s:json.dumps(s,ensure_ascii=True)
        return 'graph network {\n'+''.join(f'  {quote(n)};\n' for n in self.nodes)+''.join(f'  {quote(a)} -- {quote(b)};\n' for a,b in self.edges)+'}\n'
