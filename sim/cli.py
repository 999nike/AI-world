import argparse
from sim.core.simloop import run_sim

def main():
    p = argparse.ArgumentParser(prog="sim")
    sub = p.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run", help="Run a simulation")
    runp.add_argument("--seed", type=int, default=123)
    runp.add_argument("--ticks", type=int, default=200)
    runp.add_argument("--snapshot-every", type=int, default=10)
    runp.add_argument("--governor", type=str, default=None,
                      help="Governor command, e.g. 'focus food' or 'build hut'")
    runp.add_argument("--scenario", type=str, default=None,
                      help="Scenario commands, e.g. 'seed 42; start_food 6; event drought 100'")
    runp.add_argument("--control", type=str, default=None,
                      help="Agent ID to control, e.g. A0")
    runp.add_argument("--control-policy", type=str, default="idle",
                      help="Policy for controlled agent: gather_food, gather_wood, gather_stone, build_farm, build_hut, build_storage, idle")

    args = p.parse_args()

    if args.cmd == "run":
        run_sim(
            seed=args.seed,
            ticks=args.ticks,
            snapshot_every=args.snapshot_every,
            governor_command=args.governor,
            scenario_commands=args.scenario,
            control_agent_id=args.control,
            control_policy=args.control_policy,
        )
