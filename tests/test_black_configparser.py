import io
from typing import IO, Any, Dict
from unittest import mock

import black_configparser

# pylint:disable=protected-access


@mock.patch.object(
    black_configparser.os.path, "join", side_effect=lambda _unused, file_name: file_name
)
@mock.patch.object(black_configparser.os.path, "isfile", return_value=True)
def test_open_config_files(*_mocks: mock.MagicMock) -> None:
    open_mocks = {name: mock.mock_open() for name in black_configparser.CONFIG_FILES}

    def _mocked_open(file_name: str, *args: Any, **kwargs: Any) -> IO[str]:
        return open_mocks[file_name](file_name, *args, **kwargs)  # type:ignore

    with mock.patch("builtins.open", side_effect=_mocked_open):
        result = list(black_configparser._open_config_files())

    assert result == [
        (open_mocks[name].return_value, name)
        for name in black_configparser.CONFIG_FILES
    ]


@mock.patch.object(
    black_configparser,
    "_open_config_files",
    return_value=(
        (io.StringIO("foo"), "bar"),
        (io.StringIO("lorem"), "ipsum"),
    ),
)
def test_get_options_from_config_files(*_mocks: mock.MagicMock) -> None:
    expected_result = {
        "--file-bar": "foo",
        "--file-ipsum": "lorem",
    }

    def _mocked_get_options_from_stream(
        file_stream: IO[str], file_name: str
    ) -> Dict[str, str]:
        return {f"--file-{file_name}": file_stream.read()}

    with mock.patch.object(
        black_configparser,
        "_get_options_from_stream",
        side_effect=_mocked_get_options_from_stream,
    ):
        result = black_configparser._get_options_from_config_files()

    assert result == expected_result
