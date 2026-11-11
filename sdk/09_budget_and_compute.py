"""Read-only: your budget, billing currency, compute classes and runtimes. Changes nothing."""
import json

from _env import check_env
from wbxsandbox import compute_preferences, get_budget, runtimes

check_env()

print("budget:", json.dumps(get_budget(), indent=2))
print("compute classes:", json.dumps(compute_preferences(), indent=2))
print("runtimes:", json.dumps(runtimes(), indent=2))
