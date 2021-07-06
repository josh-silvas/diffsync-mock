"""Tasks for use with Invoke."""
import os
import sys
from invoke import task

try:
    import toml
except ImportError:
    sys.exit("Please make sure to `pip install toml` or enable the Poetry shell and run `poetry install`.")


PYPROJECT_CONFIG = toml.load("pyproject.toml")
TOOL_CONFIG = PYPROJECT_CONFIG["tool"]["poetry"]

# Can be set to a separate Python version to be used for launching or building image
PYTHON_VER = os.getenv("PYTHON_VER", "3.6")
CONTAINER_NAME = "diffsync-redis-1"


@task
def run(context, diff=True, sync=False):
    """Run the main python script to execute mocks."""
    cmd = "python main.py"
    if diff:
        cmd += " --diff"
    elif sync:
        cmd += " --sync"
    context.run(cmd, pty=True)


@task
def load_redis(context, records=5000):
    """Run build.py script to load redis with mock data.

    Args:
        records (int): Amount of mock records to add.
        context (obj): Used to run specific commands
    """
    start(context)
    cmd = f"python diffsync_mock/build.py --records {records} --redis"
    context.run(cmd, pty=True)


@task
def load_local(context, records=5000):
    """Run build.py script to generate a mock of local data.

    Args:
        records (int): Amount of mock records to add.
        context (obj): Used to run specific commands
    """
    cmd = f"python common.py --records {records} --local"
    context.run(cmd, pty=True)


@task
def container_up(context, name):
    """This will enter the image to perform troubleshooting or dev work.

    Args:
        context (obj): Used to run specific commands
        name (str): name of the container to test if up.
    """
    result = context.run(f"docker ps --filter name={name}", hide="out")
    return name in result.stdout


@task
def start(context):
    """This will enter the image to perform troubleshooting or dev work.

    Args:
        context (obj): Used to run specific commands
    """
    is_up = container_up(context, CONTAINER_NAME)
    if is_up:
        print("Redis container already running.")
        return

    print("Starting redis container.")
    context.run(f"docker run --name {CONTAINER_NAME} -p 7379:6379 -d redis", pty=True)


@task
def stop(context):
    """This will enter the image to perform troubleshooting or dev work.

    Args:
        context (obj): Used to run specific commands
    """
    is_up = container_up(context, CONTAINER_NAME)
    if not is_up:
        print("Redis container not running.")
        return

    print("Stopping redis container.")
    context.run(f"docker rm {CONTAINER_NAME}", pty=True)


@task()
def black(context):
    """Run black to check that Python files adherence to black standards."""
    exec_cmd = "black --check --diff ."
    context.run(exec_cmd, pty=True)


@task()
def flake8(context):
    """Run flake8 code analysis."""
    exec_cmd = "flake8 ."
    context.run(exec_cmd, pty=True)


@task()
def pylint(context):
    """Run pylint code analysis."""
    exec_cmd = 'find . -name "*.py" | xargs pylint'
    context.run(exec_cmd, pty=True)


@task()
def pydocstyle(context):
    """Run pydocstyle to validate docstring formatting adheres to NTC defined standards."""
    exec_cmd = "pydocstyle ."
    context.run(exec_cmd, pty=True)


@task()
def bandit(context):
    """Run bandit to validate basic static code security analysis."""
    exec_cmd = "bandit --recursive ./ --configfile .bandit.yml"
    context.run(exec_cmd, pty=True)


@task()
def tests(context):
    """Run all tests for this repository."""
    black(context)
    flake8(context)
    pylint(context)
    pydocstyle(context)
    bandit(context)

    print("All tests have passed!")
