import os
import sys


def ensure_working_directory() -> None:
    """
    Ensure the parent directory of 'scripts' is added to sys.path and
    set as the working directory.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/
    project_root = os.path.dirname(script_dir)  # src/

    if project_root not in sys.path:
        sys.path.append(project_root)

    os.chdir(project_root)
