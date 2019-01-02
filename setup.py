# -*- coding: utf-8 -*-
"""Application setup."""
import io
from setuptools import setup

with io.open('README.md', 'r', encoding='utf8') as f:
    readme = f.read()

setup(
    name='espci_bar_web_app',
    version='1.0',
    author='Samuel Diebolt',
    author_email='stryars@gmail.com',
    description='The web application for ESPCI student bar',
    license='MIT',
    long_description=readme,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
