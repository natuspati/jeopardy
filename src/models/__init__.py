import importlib
import os
import pkgutil


def import_models():
    package_dir = os.path.dirname(__file__)
    package_name = __name__

    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        full_module_name = f"{package_name}.{module_name}"
        importlib.import_module(full_module_name)


import_models()
