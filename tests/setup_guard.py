import pytest
from setup_user import *


@pytest.fixture(scope='module')
def simple_pricer(admin, SimplePricer):
    return SimplePricer.deploy(100, {'from': admin})


@pytest.fixture(scope='module')
def token(admin, MockERC20):
    return MockERC20.deploy("MockLP", "MLP", {'from': admin})


@pytest.fixture(scope='function')
def guard(admin, GuardToken, token,  simple_pricer):
    return GuardToken.deploy(token, simple_pricer, "guard", "GRD", {'from': admin})
