import pathlib
import re

from setuptools import setup, find_packages

WORK_DIR = pathlib.Path(__file__).parent


def get_version():
    """
    Read version
    :return: str
    """
    txt = (WORK_DIR / 'RelativeAddonsSystem' / '__init__.py').read_text('utf-8')
    try:
        return re.findall(r"^__version__ = \"([^\"]+)\"\r?$", txt, re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


setup(
    name='Relative Addons System',
    version=get_version(),
    packages=find_packages(),
    url='',
    license='MIT',
    author='YoungTitanium',
    author_email='youngtitanium.l@gmail.com',
    description="Easier way to manage your project addons",
    long_description='The simple python addon system, which allow you to load, reload, '
                     'enable, disable, requirements check and install of addons',
)
