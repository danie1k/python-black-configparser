import io
from textwrap import dedent

import pytest

import black_config_files

GIVEN_CONFIG_FILES = (
    (
        r"""
        [black]
        foo = True
        bar = False
        lorem = None
        ipsum = 42
        """
    ),
    (
        r"""
        [black]
        a = 1
        ; b = 2
        c = 3.14
        """
    ),
    (
        r"""
        [tools:black]
           -tools-foo-      = True
        tools-bar = False
        tools-lorem = None
        ; tools-ipsum = 42
        """
    ),
    (
        r"""
        [tools:black]
        line-length = 120
        target_version = 
          py36
          py37
          py38
        pyi = True
        skip-string-normalization = True
        include = \.pyi?$
        exclude = /(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|\.svn|_build|buck-out|build|dist)/
        """
    ),
)
EXPECTED_CONFIG_OPTIONS = (
    {
        "--foo": None,
        "--lorem": ("None",),
        "--ipsum": (42,),
    },
    {
        "-a": (1,),
        "-c": ("3.14",),
    },
    {
        "--tools-foo": None,
        "--tools-lorem": ("None",),
    },
    {
        "--line-length": (120,),
        "--target-version": ("py36", "py37", "py38"),
        "--pyi": None,
        "--skip-string-normalization": None,
        "--include": (r"\.pyi?$",),
        "--exclude": (
            r"/(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|\.svn|_build|buck-out|build|dist)/",
        ),
    },
)


@pytest.mark.parametrize(
    "given_config_file, expected_result",
    zip(GIVEN_CONFIG_FILES, EXPECTED_CONFIG_OPTIONS),
)
def test_get_options_from_stream(given_config_file, expected_result) -> None:
    file = io.StringIO(dedent(given_config_file))
    result = black_config_files._get_options_from_stream(file)
    assert result == expected_result
