import sys
import itertools

params = {
        "N": [50, 100],
        "boundary": [False, True],
        "boundary_angle": [22.5, 20, 15],
        "experiment_name": "test 1"
        }

# If we don't do this, itertools.product will treat strings as a list of characters.
normalized = {
        k: [v] if isinstance(v, str) or v is None else v
        for k, v in params.items()
        }

keys = normalized.keys()
values = normalized.values()

combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
print(combinations)

