import os
import sys


def get_env_var(name, default=None):
    try:
        return os.environ[name]
    except KeyError:
        if default is None:
            print(f"{name} environment var must be provided!")
            sys.exit(1)
        else:
            return default


def get_opt_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        return None
