from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENCE') as f:
    license = f.read()

setup(
    name='EC',
    version='0.1',
    description='Calculates easement curves to join up tracks in TS2016.',
    long_description=readme,
    author='Ewan Macpherson',
    author_email='??',
    url='??',
    license=license,
    packages=['ec']
)
