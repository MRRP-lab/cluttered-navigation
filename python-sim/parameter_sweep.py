import sys
import subprocess
import itertools
from concurrent.futures import ProcessPoolExecutor

# All keys will have a double hyphen added. Ensure these use the same form as the long argument name.
params = {
        "num": [100],
        "boundary": True,
        "boundary-angle": [22.5],
        "density": [0.2, 0.5, 1],
        "experiment-name": "EMD calc"
        }

simulator = "./generate_demo.py"
indexer = "./data/index_gen.py"

# If we don't do this, itertools.product will treat strings as a list of characters.
normalized = {
        k: [v] if isinstance(v, (str, int, float)) or v is None else v
        for k, v in params.items()
        }

keys = normalized.keys()
values = normalized.values()

combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
# print(combinations)

def run_single_sim(params):
    args = [sys.executable, simulator]
    for k, v in params.items():

        if isinstance(v, bool):
            if v:
                args.extend([f"--{k}"])
        else:
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
                "status": "SUCCESS" if result.returncode == 0 else "FAILED",
                "cmd": args
                }
    except Exception as e:
        return {**params, "status": "CRASHED", "err": str(e)}

def run_sweep(all_combinations):
    # TODO: Add progress counter
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(run_single_sim, all_combinations))

    return results

print("Running parameter sweep now.")
results = run_sweep(combinations)

full_success = True
for result in results:
    # Advanced debug
    #for k, v in result.items():
    #    print(f"{k}:", v)
    match(result["status"]):
        case "CRASHED":
            full_success = False
            print("Simulation crashed with err:")
            print(result["err"])
        case "FAILED":
            full_success = False
            print(f'Simulation failed with code {result["exit_code"]}:')
            print(result["stderr"])

if (full_success):
    print("All simulations successful!")

indexing_result = subprocess.run([sys.executable, indexer],
                                 capture_output=True,
                                 text=True,
                                 check=False
                                 )
if (indexing_result.returncode == 0):
    print("Simulation re-indexing successful.")
else:
    print(f"Simulation re-indexing unsuccessful. Exit code: {indexing_result.returncode}")

