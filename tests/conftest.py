import pytest
from environs import Env


@pytest.fixture(scope='session', autouse=True)
def read_env():
    env = Env()
    env.read_env()
