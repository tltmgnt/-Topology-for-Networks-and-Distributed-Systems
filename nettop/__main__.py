"""Analyze an undirected JSON network, optional failures and initial values."""
import argparse
import json
from pathlib import Path
from . import Network


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path,help='Write JSON report, replacing an existing file')
    parser.add_argument('--dot',type=Path,help='Write original topology as Graphviz DOT')
    parser.add_argument('--rounds',type=int,default=100)
    parser.add_argument('--tolerance',type=float,default=1e-6)
    args=parser.parse_args(argv)
    try:
        data=json.loads(args.input.read_text(encoding='utf-8'))
        if not isinstance(data,dict): raise ValueError('Input must be a JSON object')
        network=Network(data['nodes'],data['edges'])
        report={'network':network.summary()}
        failures=data.get('failures',{})
        if not isinstance(failures,dict): raise ValueError('failures must be an object')
        failed_nodes=failures.get('nodes',[]); failed_edges=failures.get('edges',[])
        if not isinstance(failed_nodes,list) or not isinstance(failed_edges,list):
            raise ValueError('Failure nodes and edges must be lists')
        surviving=network.without(failed_nodes,failed_edges)
        report['failure_analysis']=network.failure_report(failed_nodes,failed_edges)
        if 'values' in data:
            values=data['values']
            report['averaging']=network.average(values,args.rounds,args.tolerance)
            report['post_failure_averaging']=surviving.average({n:values[n] for n in surviving.nodes},args.rounds,args.tolerance)
        encoded=json.dumps(report,indent=2,allow_nan=False)+'\n'
        for path,content in [(args.output,encoded),(args.dot,network.dot())]:
            if path:
                path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding='utf-8')
        print(encoded,end='')
    except (OSError,ValueError,KeyError,TypeError,OverflowError) as exc:
        parser.error(str(exc))


if __name__=='__main__': main()
