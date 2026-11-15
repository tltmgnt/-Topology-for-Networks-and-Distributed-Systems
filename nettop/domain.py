"""Scoped synthetic domain adapter; no external execution."""
from nettop import Network

def check():
    network=Network(['a','b','c','d','e'],[['a','b'],['b','c'],['c','a'],['c','d'],['d','e']])
    failure=network.failure_report(edges=[['c','d']])
    observed=network.summary()
    return {'domain':'networks','statement':'Removing the c-d bridge in the five-node fixture leaves only a,b,c with original-membership majority capacity.',
            'passed':failure['majority_threshold']==3 and failure['majority_capable_components']==[['a','b','c']],
            'configuration':{'nodes':list(network.nodes),'edges':[list(e) for e in network.edges],'failed_edges':[['c','d']]},
            'observed':{'failure':failure,'topology':observed['topology']},'scope':'Static graph capacity; no consensus protocol liveness established'}
