import sys, os
import subprocess
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager

# So we can check the default value of strategy
from src.params import Params

_here = os.path.dirname(__file__)
SIMULATOR = os.path.join(_here, "generate_demo.py")
INDEXER = os.path.join(_here, "index_gen.py")
java_server = "./src/optimal-mrppg/bytecode/server.jar"

# All keys will have a double hyphen added. Ensure these use the same form as the long argument name.
experiments = [
    #{
    #"experiment-name": "Heatmap test",
    #"num": [n*50 for n in range(1,10)],
    #"noise": [n for n in range(0,5)],
    #"gridnum": [150],
    #"seed": [s for s in range(5)],
    #"disable-collision": False,
    #"boundary": True,
    #"boundary-angle": [22.5],
    #},
    #{
    #"experiment-name": "Gaussian test",
    #"disable-collision": [True],
    #"num": [100],
    #"gridnum": 100,
    #"row-gap": 1,
    #"pin-gap": 1,
    #"seed": 3,
    #},
    #{
    #"experiment-name": "Density Skewness",
    #"boundary": True,
    #"num": 100,
    #"density": [0.1, 0.5, 1],
    #"seed": [n for n in range(100)],
    #"noise": 1,
    #"gridnum": 100,
    #},
    #{
    #"experiment-name": "Centralized test",
    #"strategy": ["centralized"],
    #"noise": [0],
    #"row-gap": 1,
    #"pin-gap": 1,
    #"gridnum": 50,
    #"boundary": True,
    #"num": 30,
    #},
    {
    "experiment-name": "Centralized test",
    "strategy": ["centralized"],
    "seed": [n for n in range(20)],
    "noise": [1],
    "gridnum": 50,
    "boundary": True,
    "num": 30,
    },
    {
    "experiment-name": "Centralized test",
    "strategy": ["decentralized"],
    "seed": [n for n in range(200)],
    "noise": [0, 1],
    "gridnum": 50,
    "boundary": True,
    "num": 30,
    },
    #{
    #"experiment-name": "Boundary test",
    #"num": 100,
    #"gridnum": 100,
    #"boundary": True,
    #"boundary-angle": [22.5, 17.5, 12.5, 7.5, 2.5],
    #"seed": [n for n in range(100)],
    #"noise": [0, 1],
    #"row-gap": 2
    #},
]

def run_single_sim(params):
    args = [sys.executable, SIMULATOR]
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

@contextmanager
def java_solver_server(enabled=True, workers=1):
    if not enabled:
        yield None
        return
    print("Starting Java server for optimal centralized solutions.")
    proc = subprocess.Popen(["java", "-jar", java_server, str(workers)])
    try:
        yield proc
    finally:
        print("Stopping Java server.")
        proc.terminate()
        proc.wait()

def run_sims(params, all_combinations):
    needs_java = ("strategy" not in params and Params.strategy == "centralized") or \
            ("strategy" in params and "centralized" in params["strategy"])

    total = len(all_combinations)
    done = 0
    print(f"Progress: [{done}/{total}]", end="")
    results = []
    with java_solver_server(enabled=needs_java):
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(run_single_sim, p) for p in all_combinations]
            for future in as_completed(futures):
                results.append(future.result())
                done += 1
                print(f"\rProgress: [{done}/{total}]", end="", flush=True)
    print()
    return results

def full_sweep(params):
    # If we don't do this, itertools.product will treat strings as a list of characters.
    normalized = {
            k: [v] if isinstance(v, (str, int, float)) or v is None else v
            for k, v in params.items()
            }

    keys = normalized.keys()
    values = normalized.values()

    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    # print(combinations)

    print("Running parameter sweep now.")
    return run_sims(params, combinations)

def print_results(results):
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


def reindex():
    indexing_result = subprocess.run([sys.executable, INDEXER],
                                     capture_output=True,
                                     text=True,
                                     check=False
                                     )

    if (indexing_result.returncode == 0):
        print("Simulation re-indexing successful.")
    else:
        print(f"Simulation re-indexing unsuccessful. Exit code: {indexing_result.returncode}")


if __name__ == "__main__":
    experiment_num = 1
    for experiment in experiments:
        print(f"Experiment {experiment_num}: ")
        results = full_sweep(experiment)
        print_results(results)
        experiment_num += 1
    reindex()
