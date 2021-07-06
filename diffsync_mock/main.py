#!/usr/bin/env python
"""Main executable for DiffSync-Mock."""
from argparse import ArgumentParser, Namespace
from diffsync.logging import enable_console_logging

from local_adapter import LocalAdapter
from redis_adapter import RedisAdapter
from build import fetch_local_data


def main(args: Namespace):
    """Demonstrate DiffSync behavior using the example backends provided."""
    enable_console_logging(verbosity=args.verbosity)

    employees = fetch_local_data()

    print("Initializing and loading Local Data ...")
    local = LocalAdapter()
    local.load(employees)

    print("Initializing and loading Remote Data ...")
    if args.redis:
        remote = RedisAdapter()
        remote.load()
    else:
        remote = LocalAdapter()
        remote.load(employees)

    print(f"Calculating the Diff between the Local Adapter and {'Redis' if args.redis else 'Local'} Adapter ...")
    diff = remote.diff_from(local)
    print(diff.summary())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--verbosity", "-v", default=0, action="count")
    parser.add_argument(
        "--redis", help="Use Redis as an adapter store rather than in-memory allocation.", action="store_true"
    )
    main(parser.parse_args())
