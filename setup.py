# Setup.py

import re
from setuptools import setup


def get_version(init_file):
    re_ver = re.compile('^__version__\s*=\s*[\'\"](.+)[\'\"][\s\n]*$')
    with open(init_file, 'r') as initf:
        for line in initf:
            if re_ver.match(line):
                version = re_ver.match(line).group(1)
                break
        else:
            raise ValueError("__version__ not found in", init_file)

        return version


with open('README.md') as rf:
    readme = rf.read()

with open('LICENCE') as lf:
    licence = lf.read()

setup(
    name='easment-curve',
    version=get_version('ec/version.py'),
    description='Calculates easement curves to join up tracks in TS2016.',
    long_description=readme,
    author='Ewan Macpherson',
    author_email='??',
    url='https://github.com/macph/easement-curve',
    license=licence,
    packages=['ec'],
    entry_points={'gui_scripts': ['run_calc_tk = ec.main:main']}
)
