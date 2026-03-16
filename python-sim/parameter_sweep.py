import os
import sys
import subprocess
import itertools
from concurrent.futures import ProcessPoolExecutor


params = {
        "N": [50, 100],
        "boundary": [False, True],
        "boundary_angle": [22.5, 20, 15],
        "experiment_name": "test 1"
        }

simulator = "./generate_demo.py"

# If we don't do this, itertools.product will treat strings as a list of characters.
normalized = {
        k: [v] if isinstance(v, str) or v is None else v
        for k, v in params.items()
        }

keys = normalized.keys()
values = normalized.values()

combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
print(combinations)

def run_single_sim(params):
    args = [sys.executable, simulator]
    for k, v in params.items():
        args.extend([f"--{k}", str(v)])
    try:
        result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                check=False
                )

        return {
                "exit_code": result.returncode,
                "stderr": result.stderr if result.returncode != 0 else "",
                "status": "SUCCESS" if result.returncode == 0 else "FAILED"
                }
    except Exception as e:
        return {**params, "status": "CRASHED", "err": str(e)}

def run_sweep(all_combinations):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(run_single_sim, all_combinations))

    return results
