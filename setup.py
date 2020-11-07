#!/usr/bin/env python
import collections
import pathlib

from setuptools import setup

setup(
    name="black-configparser",
    version="0.1.0b2",
    author="Daniel Kuruc",
    author_email="daniel@kuruc.dev",
    license="MIT",
    url="https://github.com/danie1k/python-black-configparser",
    project_urls=collections.OrderedDict(
        (
            ("Code", "https://github.com/danie1k/python-black-configparser"),
            (
                "Issue tracker",
                "https://github.com/danie1k/python-black-configparser/issues",
            ),
        )
    ),
    description=(
        "Seamless Proxy CLI for black (\"The uncompromising code formatter\") "
        "with support for non-pyproject.toml config files"
    ),
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text("utf8"),
    long_description_content_type="text/markdown",
    keywords=(
        "automation formatter yapf autopep8 pyfmt gofmt rustfmt black white brunette"
    ),
    package_dir={"black_configparser": "src"},
    packages=["black_configparser"],
    package_data={"black_configparser": ("py.typed",)},
    python_requires=">=3.6",
    install_requires=("black>=18.6b2", "click>=6.5", "sh>=1.13.0"),
    extras_require={
        "tests": ("coverage>=5.0", "pytest>=6.0", "pytest-sugar>=0.9"),
    },
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={
        "console_scripts": ["black=black_configparser.black_configparser:main"]
    },
)
