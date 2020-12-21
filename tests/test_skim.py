import pytest
import brownie
from brownie import interface
from utils import *


def test_skim(admin, alice, eve, guard, token):
    # mint tokens to alice & bob
    mint_amt = 10 ** 70
    token.mint(alice, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': alice})

    # alice enters 3 * 10**36
    alice_enter_amt = 3 * 10**36
    print('enter', alice_enter_amt)
    tx = guard.enter(alice_enter_amt, {'from': alice})
    show_gas(tx)
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt
    assert token.balanceOf(guard) == alice_enter_amt
    assert guard.balanceOf(alice) == alice_enter_amt

    box = guard.boxes(alice)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box

    show_box(box)

    # activate & execute some portion
    activate_amt = 1 * 10**36
    tx = guard.activate(activate_amt, 0, {'from': alice})
    cover_id = tx.return_value
    assert cover_id == 0
    assert guard.balanceOf(alice) == alice_enter_amt - activate_amt
    assert guard.execute(alice, cover_id, {'from': alice})

    # skim
    prev_bal = token.balanceOf(alice)
    guard.skim({'from': alice})
    cur_bal = token.balanceOf(alice)
    assert cur_bal - prev_bal == activate_amt


def test_skim_2(admin, alice, eve, guard, token, SimplePricer):
    rate = 212
    pricer_2 = SimplePricer.deploy(100, rate * 10**18, {'from': admin})

    guard.setPricer(pricer_2, {'from': admin})

    # mint tokens to alice & bob
    mint_amt = 10 ** 70
    token.mint(alice, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': alice})

    # alice enters 3 * 10**36
    alice_enter_amt = 3 * 10**36
    print('enter', alice_enter_amt)
    tx = guard.enter(alice_enter_amt, {'from': alice})
    show_gas(tx)
    alice_guard_amt = guard.balanceOf(alice)
    print(token.balanceOf(alice))
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt * rate
    assert token.balanceOf(guard) == alice_enter_amt * rate
    assert alice_guard_amt, alice_enter_amt

    box = guard.boxes(alice)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box

    show_box(box)

    # activate & execute some portion
    activate_amt = 1 * 10**36
    tx = guard.activate(activate_amt, 0, {'from': alice})
    cover_id = tx.return_value
    assert cover_id == 0
    assert guard.balanceOf(alice) == alice_guard_amt - activate_amt
    assert guard.execute(alice, cover_id, {'from': alice})

    # skim
    prev_bal = token.balanceOf(alice)
    guard.skim({'from': alice})
    cur_bal = token.balanceOf(alice)
    assert cur_bal - prev_bal == activate_amt * rate
