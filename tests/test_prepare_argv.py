import collections
import os
from typing import Iterator
from unittest import mock

import pytest

import black_configparser

# pylint:disable=protected-access,redefined-outer-name,unused-argument

CWD = os.path.dirname(__file__)


@pytest.yield_fixture()  # type:ignore
def mock_options_getters() -> Iterator[None]:
    with mock.patch.object(
        black_configparser, "_convert_options_to_argv", return_value=True
    ) as mocked_convert_options_to_argv, mock.patch.object(
        black_configparser, "_get_options_from_config_files", return_value={}
    ) as mocked_get_options_from_config_files:
        yield

        mocked_get_options_from_config_files.assert_called_once()
        mocked_convert_options_to_argv.assert_called_once()


def test_unsupported_argument_should_raise_exception(
    mock_options_getters: Iterator[None],
) -> None:
    given_user_given_argv = ["-foo"]
    expected_error = (
        "Running black command with options is no longer supported, due to 'black-configparser'.\n"
        "Please define options in config file or use --no-config-file flag."
    )

    with pytest.raises(RuntimeError, match=expected_error):
        black_configparser._prepare_argv(given_user_given_argv)


@pytest.mark.parametrize("argument_name", ("--help", "--version"))
def test_arguments_which_should_skip_processing_arguments(
    mock_options_getters: Iterator[None], argument_name: str
) -> None:
    given_user_given_argv = [argument_name, "--foo", "bar", "--line-length=120"]
    expected_result = tuple(given_user_given_argv)

    result = black_configparser._prepare_argv(given_user_given_argv)

    assert result == expected_result


def test_no_config_flag_argument_should_skip_processing_arguments(
    mock_options_getters: Iterator[None],
) -> None:
    given_user_given_argv = [
        f"--{black_configparser.NO_CONFIG_FLAG}",
        "--foo",
        "bar",
        "--line-length=120",
    ]
    expected_result = (
        "--foo",
        "bar",
        "--line-length=120",
    )

    result = black_configparser._prepare_argv(given_user_given_argv)

    assert result == expected_result


def test_config_argument_should_raise_exception(
    mock_options_getters: Iterator[None],
) -> None:
    given_user_given_argv = ["--config"]
    expected_error = (
        "The --config flag is no longer supported, due to 'black-configparser'.\n"
        "Please define options in config file or use --no-config-file flag."
    )

    with pytest.raises(RuntimeError, match=expected_error):
        black_configparser._prepare_argv(given_user_given_argv)


@pytest.mark.parametrize("argument_name", ("--check", "--diff", "--verbose"))
def test_arguments_that_should_be_preserved(
    mock_options_getters: Iterator[None],
    argument_name: str,
) -> None:
    given_user_given_argv = [argument_name, CWD]
    expected_result = tuple(given_user_given_argv)

    result = black_configparser._prepare_argv(given_user_given_argv)

    assert result == expected_result


@pytest.mark.parametrize("argument_name", ("-c", "--code"))
def test_code_argument_should_be_preserved(
    mock_options_getters: Iterator[None], argument_name: str
) -> None:
    given_user_given_argv = [
        "--check",
        argument_name,
        'print("hello world!")',
        CWD,
    ]
    expected_result = tuple(given_user_given_argv)

    result = black_configparser._prepare_argv(given_user_given_argv)

    assert result == expected_result


@pytest.mark.parametrize(
    "pwd, path_to_check",
    (
        ("/", CWD),
        ("/home", CWD),
        (CWD, os.path.basename(__file__)),
    ),
)
def test_logic_should_allow_checking_given_path(
    mock_options_getters: Iterator[None], pwd: str, path_to_check: str
) -> None:
    given_user_given_argv = [
        "--check",
        path_to_check,
    ]
    expected_result = tuple(given_user_given_argv)

    with mock.patch.object(black_configparser, "PWD", pwd):
        result = black_configparser._prepare_argv(given_user_given_argv)

    assert result == expected_result


@pytest.mark.parametrize("given_path", ("./the/relative/path", "/absolute/path"))
def test_should_raise_exception_for_malformed_path(
    mock_options_getters: Iterator[None], given_path: str
) -> None:
    given_user_given_argv = ["--check", given_path]
    expected_error = (
        "Running black command with options is no longer supported, due to 'black-configparser'.\n"
        "Please define options in config file or use --no-config-file flag."
    )

    with pytest.raises(RuntimeError, match=expected_error):
        black_configparser._prepare_argv(given_user_given_argv)


@mock.patch.object(
    black_configparser, "_get_options_from_config_files", return_value={}
)
def test_should_skip_whole_processing_when_no_black_config_in_files(
    mocked_function: mock.MagicMock,
) -> None:
    given_user_given_argv = ["--whatever"]
    expected_result = tuple(given_user_given_argv)

    result = black_configparser._prepare_argv(given_user_given_argv)

    assert result == expected_result
    mocked_function.assert_called_once()


@mock.patch.object(
    black_configparser,
    "_get_options_from_config_files",
    return_value=collections.OrderedDict(
        (
            ("--foo", ("bar",)),
            ("--target-version", ("py33", "py34")),
            ("--pyi", None),
        )
    ),
)
def test_should_join_options_from_config_files_to_result(
    mocked_function: mock.MagicMock,
) -> None:
    given_user_given_argv = [
        "--check",
        "--code",
        'print("hello world!")',
        CWD,
    ]
    expected_result = (
        "--check",
        "--code",
        'print("hello world!")',
        "--foo",
        "bar",
        "--target-version",
        "py33",
        "--target-version",
        "py34",
        "--pyi",
        CWD,
    )

    result = black_configparser._prepare_argv(given_user_given_argv)

    assert result == expected_result
    mocked_function.assert_called_once()
