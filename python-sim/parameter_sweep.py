import sys
import subprocess
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed

# All keys will have a double hyphen added. Ensure these use the same form as the long argument name.
params = {
        "num": [30],
        "boundary": True,
        "boundary-angle": [22.5],
        "density": [0.2, 0.5, 1],
        "row-gap": [1, 2, 3, 4, 5, 6],
        "pin-gap": [1, 2, 3, 4, 5, 6],
        "noise": [0, 1, 2, 3, 4, 5],
        "seed": [s for s in range(10)],
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
    total = len(all_combinations)
    done = 0
    print(f"Progress: [{done}/{total}]", end="")
    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(run_single_sim, p) for p in all_combinations]
        for future in as_completed(futures):
            results.append(future.result())
            done += 1
            print(f"\rProgress: [{done}/{total}]", end="", flush=True)
    print()
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

