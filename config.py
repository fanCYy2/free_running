import os

import yaml

# Absolute path of the project directory.
# Everything that lives next to the code (config.yaml, the route files) is
# resolved against this instead of the current working directory, so the
# program keeps working when it is launched by absolute path -- which is the
# normal case on macOS (`sudo /path/to/venv/bin/python /path/to/main.py`) and
# also what the `spawn` based multiprocessing start method needs.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def resolve_path(path):
    """Resolve a user supplied path against the project directory.

    Absolute paths and `~` are honoured as given; relative paths are taken to
    be relative to the project, not to the shell's cwd.
    """
    path = os.path.expanduser(str(path))
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)


class Config:
    def __init__(self):
        path = os.environ.get("FREE_RUNNING_CONFIG") or resolve_path("config.yaml")
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        for i in config:
            setattr(self, i, config[i])


config = Config()
