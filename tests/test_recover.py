import pytest
import brownie
from brownie import interface


def test_recover(admin, alice, eve, mock_1, mock_2, mock_3, guard):
    mint_amt = 10 ** 18
    mock_1.mint(alice, mint_amt, {'from': admin})
    mock_2.mint(alice, mint_amt, {'from': admin})

    amt_1 = 10 ** 18
    mock_1.transfer(guard, amt_1, {'from': alice})
    # recover one-third of the amount
    guard.recover(mock_1, amt_1 // 3, {'from': admin})
    assert mock_1.balanceOf(admin) == amt_1 // 3
    # recover remaining
    guard.recover(mock_1, 2**256-1, {'from': admin})
    assert mock_1.balanceOf(admin) == amt_1

    amt_2 = 10 ** 17
    mock_2.transfer(guard, amt_2, {'from': alice})

    # eve tries to recover
    with brownie.reverts('!governor'):
        guard.recover(mock_2, 2**256-1, {'from': eve})

    guard.recover(mock_2, 2**256-1, {'from': admin})
    assert mock_2.balanceOf(admin) == amt_2
