import collections
import configparser
import os
import sys
from typing import Deque, Dict, Iterator, List, Optional, TextIO, Tuple, Union

import click
import sh

__all__ = (
    "CONFIG_FILES",
    "CONFIG_SECTIONS",
    "NO_CONFIG_FLAG",
    "PWD",
    "ParamValue",
    "ParamsType",
    "_get_options_from_config_files",
    "_get_options_from_stream",
    "_make_key",
    "_make_value",
    "_open_config_files",
    "_prepare_argv",
    "main",
)

PWD = os.getcwd()

CONFIG_FILES = ("setup.cfg", "tox.ini")
CONFIG_SECTIONS = ("black", "tools:black")
NO_CONFIG_FLAG = "no-config-file"

ParamValue = Optional[Tuple[str, ...]]
ParamsType = Dict[str, ParamValue]


def _open_config_files() -> Iterator[Tuple[TextIO, str]]:
    for file_name in CONFIG_FILES:
        file_path = os.path.join(PWD, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "r") as fobj:
                yield fobj, file_name


def _get_options_from_config_files() -> ParamsType:
    options: ParamsType = {}

    for file_stream, file_name in _open_config_files():
        options.update(_get_options_from_stream(file_stream, file_name))

    return options


def _get_options_from_stream(  # noqa:C901
    file_stream: TextIO, file_name: str
) -> ParamsType:
    result: ParamsType = {}

    config = configparser.ConfigParser()
    config.read_file(file_stream)

    for section_name in CONFIG_SECTIONS:
        if section_name not in config:
            continue

        click.secho(
            f"Using [{section_name}] configuration from {file_name}.", fg="blue"
        )

        for key, value in dict(config[section_name]).items():
            try:
                value = config.getboolean(section_name, key)  # type:ignore
            except ValueError:
                pass
            try:
                value = f"{config.getint(section_name, key)}"
            except ValueError:
                pass

            if value is False:  # type:ignore
                continue

            result[_make_key(key)] = _make_value(value)

    return result


def _make_key(value: str) -> str:
    value = value.replace("_", "-").strip(" -")
    _prefix = "-" if len(value) == 1 else "--"
    return f"{_prefix}{value}"


def _make_value(value: Union[str, bool]) -> ParamValue:
    if isinstance(value, bool):
        return None

    return tuple(filter(bool, value.strip().split("\n")))


def _prepare_argv(user_given_argv: List[str]) -> Tuple[str, ...]:  # noqa:C901
    result: Deque[str] = collections.deque()

    if "--help" in user_given_argv or "--version" in user_given_argv:
        return tuple(user_given_argv)

    if f"--{NO_CONFIG_FLAG}" in user_given_argv:
        user_given_argv.remove(f"--{NO_CONFIG_FLAG}")
        return tuple(user_given_argv)

    if "--config" in user_given_argv:
        raise RuntimeError(
            "The --config flag is no longer supported, due to 'black-configparser'.\n"
            f"Please define options in config file or use --{NO_CONFIG_FLAG} flag."
        )

    if "--check" in user_given_argv:
        user_given_argv.remove("--check")
        result.append("--check")

    if "-c" in user_given_argv or "--code" in user_given_argv:
        try:
            _code_arg_index = user_given_argv.index("-c")
        except ValueError:
            _code_arg_index = user_given_argv.index("--code")

        result += [
            user_given_argv.pop(_code_arg_index),
            user_given_argv.pop(_code_arg_index),
        ]

    for option, values_list in _get_options_from_config_files().items():
        if values_list is None:
            result.append(option)
            continue

        for value in values_list:
            result += [option, value]

    for arg in user_given_argv:
        _maybe_path = arg if os.path.isabs(arg) else os.path.join(PWD, arg)
        if not (arg[0] != "-" and os.path.exists(_maybe_path)):
            raise RuntimeError(
                "Running black command with options is no longer supported, "
                "due to 'black-configparser'.\n"
                f"Please define options in config file or use --{NO_CONFIG_FLAG} flag."
            )

        result.append(arg)

    return tuple(result)


def main() -> None:  # pragma:no cover
    argv = _prepare_argv(sys.argv[1:])
    sh.python("-m", "black", *argv, _fg=True)  # pylint:disable=no-member


if __name__ == "__main__":  # pragma:no cover
    main()
