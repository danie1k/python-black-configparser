import configparser
import os
import runpy
import sys
from typing import Dict, List, Tuple, Union, cast

import click
from black import main as black_main

CWD = os.getcwd()
CONFIG_FILES = ("setup.cfg", "tox.ini")
CONFIG_SECTION = "tools:black"

ParamsType = Dict[str, Union[None, bool, str, int, List[Union[str, int]], Tuple[str]]]


def _click_options_to_argv(options: ParamsType) -> List[str]:
    result = []

    for option_name, value in options.items():
        if value is None or value is False:
            continue

        if option_name == "src":
            continue

        if isinstance(value, (list, tuple)):
            for item in value:
                result.append(_make_argv(option_name))
                result.append(str(item))
            continue

        result.append(_make_argv(option_name))

        if value is True:
            continue

        result.append(str(value))

    # SRC positional arguments
    result += list(options["src"][1:])

    return result


def _get_current_command_options() -> ParamsType:
    black_command = click.Command(
        name=cast(click.Command, black_main).name,
        params=cast(click.Command, black_main).params,
    )
    return black_command.make_context("black", sys.argv).params


def _get_options_from_config_files() -> ParamsType:
    options: ParamsType = {}

    for file_name in CONFIG_FILES:
        file_path = os.path.join(CWD, file_name)
        if not os.path.isfile(file_path):
            continue

        config = configparser.ConfigParser()
        config.read(file_path)

        if CONFIG_SECTION not in config:
            continue

        for key, value in dict(config[CONFIG_SECTION]).items():
            try:
                value = config.getboolean(CONFIG_SECTION, key)
            except ValueError:
                pass
            try:
                value = config.getint(CONFIG_SECTION, key)
            except ValueError:
                pass

            options[_make_option(key)] = value

    return options


def _make_option(value: str) -> str:
    return value.replace("-", "_").strip(" _")


def _make_argv(value: str) -> str:
    return "--{}".format(value.replace("_", "-"))


def main():
    argv = [sys.argv[0]]
    black_options = _get_current_command_options()

    for option_name, value in _get_options_from_config_files().items():
        if option_name in ("config", "src"):
            continue
        if option_name not in black_options:
            continue

        if isinstance(black_options[option_name], list) and not isinstance(value, list):
            value = [value]

        _black_option_type = type(black_options[option_name])
        _config_option_type = type(value)
        if _black_option_type != _config_option_type:
            raise RuntimeError(
                (
                    "Type mismatch error in option '{option_name}! "
                    "Expected '{expected_type}', got '{got_type}'."
                ).format(
                    option_name=option_name,
                    expected_type=_black_option_type.__name__,
                    got_type=_config_option_type.__name__,
                )
            )

        black_options[option_name] = value

    sys.argv = argv + _click_options_to_argv(black_options)
    runpy.run_module("black")
