import argparse
from sim.core.simloop import run_sim

def main():
    p = argparse.ArgumentParser(prog="sim")
    sub = p.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run", help="Run a simulation")
    runp.add_argument("--seed", type=int, default=123)
    runp.add_argument("--ticks", type=int, default=200)
    runp.add_argument("--snapshot-every", type=int, default=10)

    args = p.parse_args()

    if args.cmd == "run":
        run_sim(seed=args.seed, ticks=args.ticks, snapshot_every=args.snapshot_every)