import pytest
import brownie
from brownie import interface, chain
from utils import *


def test_activate_and_execute(admin, alice, bob, eve, guard, token, simple_pricer):
    # mint tokens to alice & bob
    mint_amt = 10 ** 70
    token.mint(alice, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': alice})

    print(token.balanceOf(bob))
    token.mint(bob, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': bob})

    token.mint(admin, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': admin})

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

    print(token.balanceOf(guard))

    # bob activates and executes 2 * 10 ** 18
    activate_amt = 2 * 10**18
    prevTokenBalance = token.balanceOf(guard)
    tx = guard.activate(activate_amt, 0, {'from': bob})
    cover_id = tx.return_value
    assert cover_id == 0
    assert guard.balanceOf(bob) == bob_enter_amt - activate_amt
    assert guard.execute(bob, cover_id, {'from': bob})
    assert token.balanceOf(guard) == prevTokenBalance

    print(token.balanceOf(guard))

    # bob activates and executes 3 * 10 ** 18
    activate_amt_2 = 3 * 10**18
    prevTokenBalance = token.balanceOf(guard)
    tx = guard.activate(activate_amt_2, 0, {'from': bob})
    cover_id = tx.return_value
    assert cover_id == 1
    assert guard.balanceOf(bob) == bob_enter_amt - activate_amt - activate_amt_2
    simple_pricer.setPrice(200, {'from': admin})
    assert guard.execute(bob, cover_id, {'from': bob})
    assert token.balanceOf(guard) == prevTokenBalance - activate_amt_2 // 2
