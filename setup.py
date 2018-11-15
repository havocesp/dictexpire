# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import setup, find_packages

import dictexpire as pkg

exclude = ['.idea*', 'build*', '{}.egg-info*'.format(pkg.__package__), 'dist*', 'venv*', 'doc*', 'lab*']

classifiers = [
    'Development Status :: 5 - Production',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]

CWD = Path(__file__).parent.absolute()  # type: Path
ROOT_PATH = CWD.parent  # type: Path

requirements = ROOT_PATH.joinpath('requirements.txt')
requirements.touch(exist_ok=True)
requirements = requirements.read_text(encoding='utf8')
requirements = requirements.split('\n')

long_description = ROOT_PATH.joinpath('README.md')
long_description.touch(exist_ok=True)
long_description = long_description.read_text(encoding='utf8')

setup(
    name=pkg.__package__,
    version='0.1.0',
    packages=find_packages(exclude=exclude),
    url='https://github.com/havocesp/' + pkg.__package__,
    license='UNLICENSE',
    keywords='',
    author='Daniel J. Umpierrez',
    author_email='umpierrez@pm.me',
    long_description_content_type="text/markdown",
    long_description=long_description,
    description=pkg.__doc__,
    classifiers=classifiers,
    install_requires=requirements,
    dependency_links=[]
)
