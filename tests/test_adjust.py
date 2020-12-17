import pytest
import brownie
from brownie import interface
from utils import *


def test_adjust_box_adjust_all(admin, alice, bob, eve, guard, token):
    # mint tokens to alice & bob
    mint_amt = 10 ** 70
    token.mint(alice, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': alice})

    print(token.balanceOf(bob))
    token.mint(bob, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': bob})

    token.mint(admin, mint_amt, {'from': admin})
    token.approve(guard, 2**256-1, {'from': admin})

    # alice enters 3 * 10**36
    alice_enter_amt = 3 * 10**36
    print('enter', alice_enter_amt)
    tx = guard.enter(alice_enter_amt, {'from': alice})
    show_gas(tx)
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt
    assert token.balanceOf(guard) == alice_enter_amt

    box = guard.boxes(alice)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box

    show_box(box)

    # box before adjust box
    assert box_debt == 3 * 10**36
    assert box_debt_dec == 0
    assert box_fund == 3 * 10**36
    assert box_fund_dec == 0

    # global should already adjust by the end of `enter` call
    assert guard.allDebt() == 3 * 10**36 // 4  # >> 2
    assert guard.allDebtDecimals() == 2
    assert guard.allFund() == 3 * 10**36 // 4  # >> 2
    assert guard.allFundDecimals() == 2

    guard.adjustBox(alice, {'from': eve})  # adjust alice's box

    box = guard.boxes(alice)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box

    show_box(box)

    # box after adjust box
    assert box_debt == guard.allDebt()
    assert box_debt_dec == guard.allDebtDecimals()
    assert box_fund == guard.allFund()
    assert box_fund_dec == guard.allFundDecimals()

    assert guard.allDebt() == 3 * 10**36 // 4  # >> 2
    assert guard.allDebtDecimals() == 2
    assert guard.allFund() == 3 * 10**36 // 4  # >> 2
    assert guard.allFundDecimals() == 2

    # alice re-enters 10 ** 39
    alice_reenter_amt = 10 ** 39

    print('enter', alice_reenter_amt)
    tx = guard.enter(alice_reenter_amt, {'from': alice})
    show_gas(tx)
    assert token.balanceOf(alice) == mint_amt - alice_enter_amt - alice_reenter_amt
    assert token.balanceOf(guard) == alice_enter_amt + alice_reenter_amt

    box = guard.boxes(alice)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box

    show_box(box)

    assert box_debt == (3 * 10**36 + 10**39) // 4
    assert box_debt_dec == 2
    assert box_fund == (3 * 10**36 + 10**39) // 4
    assert box_fund_dec == 2

    assert guard.allDebt() == (3 * 10**36 + 10**39) // (2**10)
    assert guard.allDebtDecimals() == 10
    assert guard.allFund() == (3 * 10**36 + 10**39) // (2**10)
    assert guard.allFundDecimals() == 10

    guard.adjustBox(alice, {'from': alice})  # adjust alice's box

    box = guard.boxes(alice)
    box_debt, box_debt_dec, box_fund, box_fund_dec = box

    show_box(box)

    assert box_debt == (3 * 10**36 + 10**39) // (2**10)
    assert box_debt_dec == 10
    assert box_fund == (3 * 10**36 + 10**39) // (2**10)
    assert box_fund_dec == 10

    assert guard.allDebt() == (3 * 10**36 + 10**39) // (2**10)
    assert guard.allDebtDecimals() == 10
    assert guard.allFund() == (3 * 10**36 + 10**39) // (2**10)
    assert guard.allFundDecimals() == 10
