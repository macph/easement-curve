from setuptools import setup


with open('README') as f:
    readme = f.read()

with open('LICENCE') as f:
    licence = f.read()

setup(
    name='easment-curve',
    version='0.1',
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
