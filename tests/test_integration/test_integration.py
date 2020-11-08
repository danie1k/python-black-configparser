import os
import runpy
import sys
from distutils.spawn import find_executable
from unittest import mock

import click
import pytest
from _pytest.capture import CaptureFixture

try:
    from black_configparser import (  # pylint:disable=unused-import  # noqa:F401
        black_configparser,
    )
except ImportError:
    pytest.skip(
        "The 'black_configparser.black_configparser' package is not installed",
        allow_module_level=True,
    )


def test_if_console_command_installed_correctly() -> None:
    with open(find_executable("black"), "r") as fobj:  # type:ignore
        black_bin_file = fobj.read()

    assert (
        "black_configparser" in black_bin_file or "black-configparser" in black_bin_file
    )


@mock.patch("click.Command.invoke")
def test_if_argument_from_config_file_are_passed_to_black(
    click_command_invoke_mock: mock.MagicMock,
    capsys: CaptureFixture,  # type:ignore
) -> None:
    os.chdir(os.path.dirname(__file__))
    with pytest.raises(SystemExit), mock.patch.object(
        sys, "argv", ["black", "--verbose", os.path.basename(__file__)]
    ):
        runpy.run_module("black_configparser.black_configparser", run_name="__main__")

    assert click_command_invoke_mock.call_count >= 1
    expected_to_be_black = click_command_invoke_mock.mock_calls[0]
    click_context: click.Context = expected_to_be_black[1][0]

    assert click_context.params["exclude"] == "/foo,bar/"  # See ./setup.cfg
    assert click_context.params["verbose"] is True

    captured = capsys.readouterr()
    assert captured.err.startswith("Using [black] configuration from setup.cfg.\n")
