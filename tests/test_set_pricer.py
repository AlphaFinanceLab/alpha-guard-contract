import pytest
import brownie
from brownie import interface


def test_set_pricer(admin, eve, guard, simple_pricer, SimplePricer):
    assert guard.pricer() == simple_pricer
    assert interface.IPricer(guard.pricer()).getCurrentPrice() == 100
    # set to another pricer
    fake_pricer = SimplePricer.deploy(0, {'from': admin})
    guard.setPricer(fake_pricer, {'from': admin})

    assert guard.pricer() == fake_pricer
    assert interface.IPricer(guard.pricer()).getCurrentPrice() == 0

    # set back to original pricer
    guard.setPricer(simple_pricer, {'from': admin})

    assert guard.pricer() == simple_pricer
    assert interface.IPricer(guard.pricer()).getCurrentPrice() == 100

    # eve tries to set pricer
    with brownie.reverts('!governor'):
        guard.setPricer(fake_pricer, {'from': eve})

    assert guard.pricer() == simple_pricer
    assert interface.IPricer(guard.pricer()).getCurrentPrice() == 100
