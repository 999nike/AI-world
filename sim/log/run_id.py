from datetime import datetime
import random
import string

def make_run_id() -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    suffix = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{ts}_{suffix}"