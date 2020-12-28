import pytest
import brownie
from brownie import interface, chain
from utils import *


def test_exit_and_claim(admin, alice, bob, eve, guard, token):
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

    # bob activates and executes 2 * 10 ** 18
    activate_amt = 2 * 10**18
    tx = guard.activate(activate_amt, 0, {'from': bob})
    cover_id = tx.return_value
    assert cover_id == 0
    assert guard.balanceOf(bob) == bob_enter_amt - activate_amt
    assert guard.execute(bob, cover_id, {'from': bob})

    # alice re-enters 4 * 10 ** 18
    alice_reenter_amt = 4 * 10 ** 18
    print('re-enter', alice_reenter_amt)
    tx = guard.enter(alice_reenter_amt, {'from': alice})
    show_gas(tx)
    show_box(guard.boxes(alice))
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt - alice_reenter_amt
    assert token.balanceOf(guard) == alice_enter_amt + bob_enter_amt + \
        alice_reenter_amt

    # alice exits 1 * 10 ** 18 (not claim yet)
    alice_exit_amt = 10**18
    prevTotalSupply = guard.totalSupply()
    tx = guard.exit(alice_exit_amt, {'from': alice})
    show_gas(tx)
    alice_receipt_id = tx.return_value
    curTotalSupply = guard.totalSupply()
    show_gas(tx)
    show_box(guard.boxes(alice))

    assert token.balanceOf(alice) == mint_amt - alice_enter_amt - alice_reenter_amt
    assert token.balanceOf(guard) == alice_enter_amt + bob_enter_amt + \
        alice_reenter_amt
    assert curTotalSupply - prevTotalSupply == - (alice_exit_amt * 10 // 12)

    # alice tries to claim immediately
    with brownie.reverts('!valid'):
        tx = guard.claim(alice_receipt_id, {'from': alice})

    chain.sleep(14 * 86400)  # 14 days passed

    # alice claims
    show_box(guard.boxes(alice))
    tx = guard.claim(alice_receipt_id, {'from': alice})
    show_gas(tx)
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt - \
        alice_reenter_amt + alice_exit_amt * 70 // 78
    assert token.balanceOf(guard) == alice_enter_amt + bob_enter_amt + \
        alice_reenter_amt - alice_exit_amt * 70 // 78
