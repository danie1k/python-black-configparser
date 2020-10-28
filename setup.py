#!/usr/bin/env python
import os

from setuptools import setup


def get_long_description() -> str:
    path = os.path.join(os.path.dirname(__file__), "README.md")
    with open(path, encoding="utf8") as fobj:
        return fobj.read()


setup(
    name="black_config_files",
    version="0.0.2",
    description=(
        "Proxy CLI for black (The uncompromising code formatter) "
        "with support for setup.cfg & tox.ini config files"
    ),
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords=(
        "automation formatter yapf autopep8 pyfmt gofmt rustfmt black white brunette"
    ),
    author="Daniel Kuruc",
    author_email="daniel@kuruc.dev",
    url="https://github.com/danie1k/black_config_files",
    license="MIT",
    py_modules=["black_config_files"],
    python_requires=">=3.6",
    zip_safe=False,
    install_requires=["black>=18.6b2", "click>=6.5"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={"console_scripts": ["black=black_config_files:main"]},
)
