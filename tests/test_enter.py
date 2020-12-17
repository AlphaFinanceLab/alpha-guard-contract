import pytest
import brownie
from brownie import interface
from utils import *


def test_enter(admin, alice, bob, eve, guard, token):
    # mint tokens to alice & bob
    mint_amt = 10 ** 70
    token.mint(alice, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': alice})

    print(token.balanceOf(bob))
    token.mint(bob, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': bob})

    token.mint(admin, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': admin})

    # enter 0
    print('enter 0')
    tx = guard.enter(0, {'from': alice})
    show_gas(tx)
    assert token.balanceOf(alice) == mint_amt
    assert token.balanceOf(guard) == 0

    # alice enters 3 * 10 ** 18
    alice_enter_amt = 3 * 10 ** 18
    print('enter', alice_enter_amt)
    tx = guard.enter(alice_enter_amt, {'from': alice})
    show_gas(tx)
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt
    assert token.balanceOf(guard) == alice_enter_amt

    box = guard.boxes(alice)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box
    show_box(box)
    guard.adjustBox(alice, {'from': eve})
    assert box_debt == guard.allDebt()
    assert box_debt_dec == guard.allDebtDecimals()
    assert box_fund == guard.allFund()
    assert box_fund_dec == guard.allFundDecimals()

    # bob enters 9 * 10 ** 18
    bob_enter_amt = 9 * 10 ** 18
    print('enter', bob_enter_amt)
    tx = guard.enter(bob_enter_amt, {'from': bob})
    show_gas(tx)
    assert token.balanceOf(bob) == mint_amt - bob_enter_amt
    assert token.balanceOf(guard) == alice_enter_amt + bob_enter_amt

    box = guard.boxes(bob)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box
    show_box(box)
    guard.adjustBox(alice, {'from': bob})
    assert box_debt == bob_enter_amt
    assert box_debt_dec == 0
    assert box_fund == bob_enter_amt
    assert box_fund_dec == 0

    # alice re-enters 4 * 10 ** 18
    alice_reenter_amt = 4 * 10 ** 18
    print('re-enter', alice_reenter_amt)
    tx = guard.enter(alice_reenter_amt, {'from': alice})
    show_gas(tx)
    show_box(guard.boxes(alice))
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt - alice_reenter_amt
    assert token.balanceOf(guard) == alice_enter_amt + bob_enter_amt + alice_reenter_amt

    # time passes, the ratio changes
    # fake by stealing 9999/10000 tokens from guard
    guard.recover(token, token.balanceOf(guard) * 9999 // 10000, {'from': admin})
    print(token.balanceOf(guard))

    print('Alice box')
    show_box(guard.boxes(alice))
    print('Bob box')
    show_box(guard.boxes(bob))

    # bob re-enters 5 * 10 ** 18
    bob_reenter_amt = 5 * 10 ** 18
    print('re-enter', bob_reenter_amt)
    tx = guard.enter(bob_reenter_amt, {'from': bob})
    show_gas(tx)
    show_box(guard.boxes(bob))
    assert token.balanceOf(bob) == mint_amt - bob_enter_amt - bob_reenter_amt
    assert token.balanceOf(guard) == (alice_enter_amt + alice_reenter_amt +
                                      bob_enter_amt) // 10000 + bob_reenter_amt

    assert guard.boxes(bob)[2] == bob_enter_amt + 10000 * bob_reenter_amt
