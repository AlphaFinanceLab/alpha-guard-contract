import pytest


@pytest.fixture(scope='function')
def mock_1(admin, MockERC20):
    return MockERC20.deploy("mock_1", "M_1", {'from': admin})


@pytest.fixture(scope='function')
def mock_2(admin, MockERC20):
    return MockERC20.deploy("mock_2", "M_2", {'from': admin})


@pytest.fixture(scope='function')
def mock_3(admin, MockERC20):
    return MockERC20.deploy("mock_3", "M_3", {'from': admin})
