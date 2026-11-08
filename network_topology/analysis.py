"""Bounded synchronous min-flooding with static node/edge failure scenarios."""

def reachable(start,nodes,edges):
    found={start};pending=[start]
    while pending:
        node=pending.pop()
        for a,b in edges:
            if a==node and b not in found:found.add(b);pending.append(b)
    return found


def analyze(data):
    if not isinstance(data,dict) or set(data)!={'schema_version','nodes','edges','initial','failure_budget'} or type(data['schema_version']) is not int or data['schema_version']!=1:raise ValueError('exact network schema_version 1 required')
    nodes,edges,initial=data['nodes'],data['edges'],data['initial']
    if not isinstance(nodes,list) or not 1<=len(nodes)<=12 or any(not isinstance(n,str) or not n or len(n)>32 for n in nodes) or len(set(nodes))!=len(nodes):raise ValueError('1..12 unique node IDs required')
    if not isinstance(edges,list) or len(edges)>32 or any(not isinstance(e,list) or len(e)!=2 or any(n not in nodes for n in e) or e[0]==e[1] for e in edges):raise ValueError('at most 32 directed non-self edges required')
    if len({tuple(e) for e in edges})!=len(edges):raise ValueError('duplicate edge')
    if not isinstance(initial,dict) or set(initial)!=set(nodes) or any(type(v) is not int or abs(v)>1000000 for v in initial.values()):raise ValueError('bounded integer initial values for every node required')
    if type(data['failure_budget']) is not int or data['failure_budget'] not in (0,1):raise ValueError('failure_budget must be 0 or 1')
    nodes=sorted(nodes);edges=sorted(tuple(e) for e in edges)
    scenarios=[('baseline',None,None)]
    if data['failure_budget']:
        scenarios += [('node:'+n,n,None) for n in nodes]
        scenarios += [('edge:'+a+'->'+b,None,(a,b)) for a,b in edges]
    results=[]
    for label,removed_node,removed_edge in scenarios:
        active=[n for n in nodes if n!=removed_node]
        links=[e for e in edges if removed_node not in e and e!=removed_edge]
        values={n:initial[n] for n in active};history=[dict(values)];messages=0
        for _ in range(max(0,len(active)-1)):
            next_values=dict(values)
            for a,b in links:next_values[b]=min(next_values[b],values[a]);messages+=1
            values=next_values;history.append(dict(values))
        expected={n:min(initial[s] for s in active if n in reachable(s,active,links)) for n in active}
        if values!=expected:raise ValueError('independent reachability oracle mismatch')
        agreement=bool(active) and len(set(values.values()))==1
        results.append({'scenario':label,'active_nodes':active,'final':values,'oracle':expected,'agreement':agreement,
                        'not_applicable':not active,'rounds':max(0,len(active)-1),'messages':messages,'history':history,
                        'strongly_connected':bool(active) and all(len(reachable(n,active,links))==len(active) for n in active)})
    failures=[r['scenario'] for r in results if not r['agreement'] and not r['not_applicable']]
    return {'schema_version':1,'domain':'networks','status':'FAIL' if failures else 'PASS','scenarios':results,'agreement_failures':failures,
            'execution_authorized':False,
            'scope':'Synchronous reliable directed links; only one static pre-start node or edge outage at a time. Min of reachable initial values after n-1 rounds. No asynchronous, Byzantine, delay, crash-during-run, deployment or general consensus-solvability claim.'}
