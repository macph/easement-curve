# Setup.py

import re
from setuptools import setup


def get_version(version_file):
    re_ver= re.compile('^__version__\s*=\s*[\'\"](.+)[\'\"][\s\n]*$')
    with open(version_file, 'r') as initf:
        for line in initf:
            if line.startswith('__version__'):
                version = re_ver.search(line).group(1)
                break
        else:
            raise ValueError("__version__ not found in", version_file)

        return version


with open('README.md') as rf:
    readme = rf.read()

with open('LICENCE') as lf:
    licence = lf.read()

setup(
    name='easment-curve',
    version=get_version('ec/__init__.py'),
    description='Calculates easement curves to join up tracks in TS2016.',
    long_description=readme,
    author='Ewan Macpherson',
    author_email='??',
    url='https://github.com/macph/easement-curve',
    license=licence,
    packages=['ec'],
    entry_points={
        'console_scripts': ['run_calc_cli = ec.interface_cli:main'],
        'gui_scripts': ['run_calc_tk = ec.interface_tk:main']
    }
)