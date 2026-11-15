"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")




def run():
    from network_topology.analysis import analyze
    def model(edges, values):
        return {"schema_version":1,"nodes":list("abc"),"edges":edges,"initial":values,"failure_budget":0}
    edges = [["a","b"],["b","c"]]
    r = analyze(model(edges, {"a":3,"b":2,"c":1}))
    check("minimum cannot flow backwards", r["scenarios"][0]["final"], {"a":3,"b":2,"c":1})
    check("directed chain can disagree", r["status"], "FAIL")
    r = analyze(model(edges, {"a":0,"b":1,"c":2}))
    check("smallest upstream value reaches all", r["scenarios"][0]["final"], {"a":0,"b":0,"c":0})
    check("agreement is value-dependent", r["status"], "PASS")
    check("agreement is not strong connectivity", r["scenarios"][0]["strongly_connected"], False)
    rejects("duplicate directed edge", lambda: analyze(model(edges + [["a","b"]], {"a":0,"b":1,"c":2})))
    check("no deployment authority", r["execution_authorized"], False)

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
