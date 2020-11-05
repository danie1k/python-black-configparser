import configparser
import os
import sys
from typing import Any, Dict, Iterator, List, Optional, TextIO, Tuple, Union

import click
import sh

CWD = os.getcwd()
CONFIG_FILES = ("setup.cfg", "tox.ini")
CONFIG_SECTIONS = ("black", "tools:black")
NO_CONFIG_FLAG = "no-config-file"


ParamValue = Optional[Tuple[Union[str, int], ...]]
ParamsType = Dict[str, ParamValue]


def _open_config_files() -> Iterator[TextIO]:
    for file_name in CONFIG_FILES:
        file_path = os.path.join(CWD, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "r") as fobj:
                yield fobj


def _get_options_from_config_files():
    options: ParamsType = {}

    for file_stream in _open_config_files():
        options.update(_get_options_from_stream(file_stream))

    return options


def _get_options_from_stream(file_stream: TextIO) -> ParamsType:
    result: ParamsType = {}

    config = configparser.ConfigParser()
    config.read_file(file_stream)

    for section_name in CONFIG_SECTIONS:
        if section_name not in config:
            continue

        for key, value in dict(config[section_name]).items():
            try:
                value = config.getboolean(section_name, key)
            except ValueError:
                pass
            try:
                value = config.getint(section_name, key)
            except ValueError:
                pass

            if value is False:
                continue

            result[_make_key(key)] = _make_value(value)

    return result


def _make_key(value: str) -> str:
    value = value.replace("_", "-").strip(" -")
    _prefix = "-" if len(value) == 1 else "--"
    return f"{_prefix}{value}"


def _make_value(value: Union[str, int, bool]) -> ParamValue:
    if value is True:
        return None

    if isinstance(value, str):
        value = value.strip().split("\n")

    if not isinstance(value, (list, tuple)):
        value = [value]

    return tuple(filter(bool, value))


def _run_black(arguments: List[Union[str, int]] = None) -> None:
    sh.python("-m", "black", *(arguments or sys.argv[1:]), _fg=True)


def main():
    argv = sys.argv  # type: List[Any]

    if "--help" in argv:
        return _run_black()

    # --check
    # --code

    if f"--{NO_CONFIG_FLAG}" in argv:
        argv.remove(f"--{NO_CONFIG_FLAG}")
        return _run_black(argv)

    for arg in argv:
        if arg[0] == "-" and not os.path.exists(os.path.join(CWD, arg)):
            click.echo(
                (
                    "Running black command with options is no longer supported.\n"
                    f"Please define options in config file or use --{NO_CONFIG_FLAG} flag."
                ),
                err=True,
            )
            sys.exit(1)

    for option, values_list in _get_options_from_config_files().items():
        if values_list is None:
            argv.append(option)
            continue

        for value in values_list:
            argv += [option, value]

    return _run_black(argv)


if __name__ == "__main__":
    main()
