import argparse
from sim.core.simloop import run_sim


EXAMPLES = """
examples:
  python -m sim run --seed 42 --ticks 300
  python -m sim run --agents 6 --seed 42
  python -m sim run --governor "focus food"
  python -m sim run --scenario "seed 42; start_food 6; event drought 120"
  python -m sim run --control A0 --control-policy gather_food
  python -m sim run --agents 6 --governor "focus expand" --scenario "seed 7; event boom 80"
  python -m sim run --playable --seed 42 --ticks 2000
  python -m sim run --playable --choice-policy seeded --seed 42 --ticks 2000
  python -m sim run --playable --rival --seed 42 --ticks 2500
"""


def main():
    p = argparse.ArgumentParser(
        prog="sim",
        description="AI-world — deterministic civilisation simulation lab",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser(
        "run",
        help="Run a simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES,
    )

    # Core
    runp.add_argument(
        "--seed", type=int, default=123,
        help="Random seed (default: 123). Same seed = same outcome.",
    )
    runp.add_argument(
        "--ticks", type=int, default=200,
        help="How many ticks to simulate (default: 200)",
    )
    runp.add_argument(
        "--snapshot-every", type=int, default=10,
        help="Save a world snapshot every N ticks (default: 10)",
    )
    runp.add_argument(
        "--agents", type=int, default=4,
        help="Number of agents to spawn (default: 4)",
    )

    # Human roles
    runp.add_argument(
        "--governor", type=str, default=None, metavar="CMD",
        help="Soft preference for all agents. Examples: 'focus food', 'build hut', 'focus expand', 'clear'",
    )
    runp.add_argument(
        "--scenario", type=str, default=None, metavar="CMDS",
        help="Starting conditions + timed events, separated by ';'. "
             "Examples: 'seed 42; start_food 6', 'agents 6; event drought 120', 'event boom 80'",
    )
    runp.add_argument(
        "--control", type=str, default=None, metavar="AGENT",
        help="Take direct control of one agent (e.g. A0, A1, A2)",
    )
    runp.add_argument(
        "--control-policy", type=str, default="idle", metavar="POLICY",
        help="What the controlled agent does: "
             "gather_food, gather_wood, gather_stone, "
             "build_farm, build_hut, build_storage, idle (default: idle)",
    )
    runp.add_argument(
        "--playable", action="store_true",
        help="Pause at fat moments and pick a governor edict (food / science / army).",
    )
    runp.add_argument(
        "--choice-policy", type=str, default="human",
        choices=["human", "first", "seeded"],
        help="How edicts are picked when --playable (default: human). "
             "first=always feed; seeded=deterministic from seed.",
    )

    runp.add_argument(
        "--rival", action="store_true",
        help="Spawn a rival civ on the far side of the map (4 agents, own governor).",
    )

    args = p.parse_args()

    if args.cmd == "run":
        run_sim(
            seed=args.seed,
            ticks=args.ticks,
            snapshot_every=args.snapshot_every,
            num_agents=args.agents,
            governor_command=args.governor,
            scenario_commands=args.scenario,
            control_agent_id=args.control,
            control_policy=args.control_policy,
            playable=args.playable,
            choice_policy=args.choice_policy if args.playable else "first",
            rival_agents=4 if args.rival else 0,
        )


if __name__ == "__main__":
    main()
