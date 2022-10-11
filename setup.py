from setuptools import setup, find_packages

import RelativeAddonsSystem

setup(
    name='Relative Addons System',
    version=RelativeAddonsSystem.__version__,
    packages=find_packages(),
    url='',
    license='MIT',
    author='YoungTitanium',
    author_email='youngtitanium.l@gmail.com',
    description='The simple python addon system, which allow you to load, reload, enable, disable, requirements check and install of addons'
)
