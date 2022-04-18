#!/bin/env python

import os
import sys
from pathlib import Path


def python_module_to_dir(module: str) -> str:
    parsed_dir = '/'.join(module.split('.'))
    return Path(f'./{parsed_dir}').resolve()


def help_command():
    print('Usage:')
    print('   `pipenv run cov breathecode.events` where events is the name of module and accept '
          'add submodules using the dot(.) character as delimiter.')
    print('')
    print('commands:')
    print('   --help see this help message.')
    exit()


if __name__ == '__main__':
    module = 'breathecode'

    if len(sys.argv) > 1:
        module = sys.argv[1]

        if module == '--help' or module == '-h':
            help_command()

    dir = python_module_to_dir(module)

    xml_path = os.path.join(os.getcwd(), 'coverage.xml')

    if os.path.exists(xml_path):
        os.remove(xml_path)

    exit_code = os.system(f'pytest {dir} --disable-pytest-warnings --cov={module} --cov-report xml -n auto')

    # python don't return 256
    if exit_code:
        sys.exit(1)
