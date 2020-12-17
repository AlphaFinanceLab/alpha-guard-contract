import pytest
import brownie
from brownie import interface


def test_governor(admin, guard):
    assert guard.governor() == admin


def test_pending_governor(guard):
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_set_governor(admin, alice, guard):
    assert guard.governor() == admin
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # set pending governor to alice
    guard.setPendingGovernor(alice, {'from': admin})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == alice
    # accept governor
    guard.acceptGovernor({'from': alice})
    assert guard.governor() == alice
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_not_governor(admin, alice, bob, eve, guard):
    assert guard.governor() == admin
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # not governor tries to set governor
    with brownie.reverts('!governor'):
        guard.setPendingGovernor(bob, {'from': alice})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # admin sets self
    guard.setPendingGovernor(admin, {'from': admin})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == admin
    # accept self
    guard.acceptGovernor({'from': admin})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # governor sets another
    guard.setPendingGovernor(alice, {'from': admin})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == alice
    # alice tries to set without accepting
    with brownie.reverts('!governor'):
        guard.setPendingGovernor(admin, {'from': alice})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == alice
    # eve tries to accept
    with brownie.reverts('!pendingGovernor'):
        guard.acceptGovernor({'from': eve})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == alice
    # alice accepts governor
    guard.acceptGovernor({'from': alice})
    assert guard.governor() == alice
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'


def test_governor_set_twice(admin, alice, eve, guard):
    assert guard.governor() == admin
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'
    # mistakenly set eve to governor
    guard.setPendingGovernor(eve, {'from': admin})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == eve
    # set another governor before eve can accept
    guard.setPendingGovernor(alice, {'from': admin})
    assert guard.governor() == admin
    assert guard.pendingGovernor() == alice
    # eve can no longer accept governor
    with brownie.reverts('!pendingGovernor'):
        guard.acceptGovernor({'from': eve})
    # alice accepts governor
    guard.acceptGovernor({'from': alice})
    assert guard.governor() == alice
    assert guard.pendingGovernor() == '0x0000000000000000000000000000000000000000'
