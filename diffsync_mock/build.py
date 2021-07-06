"""Build script used to populate a mock data source."""
import json
import os

from argparse import ArgumentParser
from typing import List, Dict
from redis import Redis
from faker import Faker
from diffsync_mock.const import LOCAL_FILE_NAME, REDIS_PORT, REDIS_HOST, RECORDS, LOGGER


def generate_data(records: int = RECORDS) -> List[Dict]:
    """generate_data function will initialize a Faker instance and generate random employee records.

    Args:
        records (int): Amount of records to generate.
    """
    LOGGER.info("Generating %s random records...", records)

    fake = Faker()
    data = []

    for _ in range(records):
        data.append(fake.profile(fields=["job", "company", "ssn", "residence", "username", "name", "mail"]))

    return data


def fetch_local_data() -> List[Dict]:
    """fetch_local_data function will load the generated 'local' data into memory."""
    if not os.path.isfile(LOCAL_FILE_NAME):
        raise FileNotFoundError(f"'{LOCAL_FILE_NAME}' file not found. Please run 'invoke load-local' first!")
    with open(LOCAL_FILE_NAME, "r") as file:
        return json.loads(file.read())


def populate_redis(records: int = RECORDS):
    """Simple function used to generate data and populate redis.

    The 'username' field is used as the redis key for each record.
    """
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
    if redis.flushall():
        print("Flushed all keys from diffsync redis instance.")

    data = generate_data(records=records)
    for index, item in enumerate(data):
        item["username"] = f"{item['username']}{index}"
        redis.hset(item["username"], None, None, item)


def populate_local(records: int = RECORDS):
    """Simple function used to generate data and populate the local json file store."""
    data = generate_data(records=records)
    with open(LOCAL_FILE_NAME, "w") as file:
        json.dump(data, file, indent=2)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--records", default=RECORDS, help="Amount of records to add to redis.")
    parser.add_argument("--redis", help="Load data into redis.", action="store_true")
    parser.add_argument("--local", help="Load data into local store (.json file).", action="store_true")
    args = parser.parse_args()
    if args.redis:
        populate_redis(int(args.records))
    elif args.local:
        populate_local(int(args.records))
    else:
        raise ValueError("Must pass in either `--redis` or `--local` as object store!")
