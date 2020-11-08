import os
import sys

from _pytest.config import Config


def pytest_configure(config: Config) -> None:  # pylint:disable=unused-argument
    sys.path.append(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, "black_configparser")
        )
    )
