from typing import List, Dict, Any

import rtamt


def monitor_trace(stl_spec: str, vars: List[str], types: List[str], trace: Dict[str, Any]):
    spec = rtamt.STLSpecification()
    for v, t in zip(vars, types):
        spec.declare_var(v, f'{t}')
    spec.spec = stl_spec
    try:
        spec.parse()
    except rtamt.STLParseException as err:
        print(f"[Error] STL Spec cannot be parsed by rtamt:\n{err}")
        return
    # preprocess format, evaluate, post process
    robustness_trace = spec.evaluate(trace)
    return robustness_trace
