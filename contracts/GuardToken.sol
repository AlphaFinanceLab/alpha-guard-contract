pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/ERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/SafeERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/utils/ReentrancyGuard.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/SafeMath.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/Math.sol';
import '../interfaces/IPricer.sol';

contract GuardToken is ERC20, ReentrancyGuard {
  using SafeERC20 for IERC20;

  event AdjustDebtDecimals(uint decimals);
  event AdjustFundDecimals(uint decimals);

  event Enter(address owner, uint count, uint value, uint debt, uint fund);
  event Skim(address owner, uint back, uint less);
  event Exit(address owner, uint id, uint count, uint debt, uint fund);
  event Execute(address caller, address owner, uint id, uint payout, uint bounty);
  event Activate(address owner, uint id, uint count, uint duration, uint spending);
  event Claim(address owner, uint id, uint value);

  uint public constant BOUNTY_BPS_START = 500;
  uint public constant BOUNTY_BPS_GROW = 9500;
  uint public constant BOUNTY_DECAY_PERIOD = 24 hours;
  uint public constant RECEIPT_WAIT_PERIOD = 14 days;

  struct Box {
    uint debt;
    uint debtDecimals;
    uint fund;
    uint fundDecimals;
  }

  struct Cover {
    uint count;
    uint spending;
    uint startPrice;
    uint expiredAt;
  }

  struct Receipt {
    uint validAt;
    uint fund;
    uint fundDecimals;
  }

  IERC20 public immutable token;
  IPricer public pricer;

  mapping(address => Box) public boxes;
  mapping(address => Cover[]) public covers;
  mapping(address => Receipt[]) public receipts;

  uint public allDebt;
  uint public allDebtDecimals;
  uint public allFund;
  uint public allFundDecimals;
  address public governor;
  address public pendingGovernor;

  constructor(
    IERC20 _token,
    IPricer _pricer,
    string memory name,
    string memory symbol
  ) public ERC20(name, symbol) {
    token = _token;
    pricer = _pricer;
    governor = msg.sender;
  }

  function setPricer(IPricer _pricer) external {
    require(msg.sender == governor, '!governor');
    pricer = _pricer;
  }

  function setPendingGovernor(address _pendingGovernor) external {
    require(msg.sender == governor, '!governor');
    pendingGovernor = _pendingGovernor;
  }

  function acceptGovernor() external {
    require(msg.sender == pendingGovernor, '!pendingGovernor');
    governor = msg.sender;
    pendingGovernor = address(0);
  }

  function recover(IERC20 what, uint amount) external {
    require(msg.sender == governor, '!governor');
    what.transfer(msg.sender, amount == uint(-1) ? what.balanceOf(address(this)) : amount);
  }

  function adjustBox(address user) public {
    Box storage box = boxes[user];
    box.debt >>= (allDebtDecimals - box.debtDecimals);
    box.fund >>= (allFundDecimals - box.fundDecimals);
    box.debtDecimals = allDebtDecimals;
    box.fundDecimals = allFundDecimals;
  }

  function adjustAll() public {
    uint _allDebt = allDebt;
    if (_allDebt > 1e36) {
      uint _allDebtDecimals = allDebtDecimals;
      while (_allDebt > 1e36) {
        _allDebt >>= 1;
        _allDebtDecimals++;
      }
      allDebt = _allDebt;
      allDebtDecimals = _allDebtDecimals;
      emit AdjustDebtDecimals(_allDebtDecimals);
    }
    uint _allFund = allFund;
    if (_allFund > 1e36) {
      uint _allFundDecimals = allFundDecimals;
      while (_allFund > 1e36) {
        _allFund >>= 1;
        _allFundDecimals++;
      }
      allFund = _allFund;
      allFundDecimals = _allFundDecimals;
      emit AdjustFundDecimals(_allFundDecimals);
    }
  }

  function enter(uint count) external nonReentrant {
    adjustBox(msg.sender);
    Box storage box = boxes[msg.sender];
    uint supply = totalSupply();
    uint wealth = token.balanceOf(address(this));
    uint value = pricer.getMaxPayout(count);
    uint debt = allDebt == 0 || supply == 0 ? count : count.mul(allDebt).div(supply);
    uint fund = allFund == 0 || wealth == 0 ? value : value.mul(allFund).div(wealth);
    _mint(msg.sender, count);
    token.transferFrom(msg.sender, address(this), value);
    box.debt = box.debt.add(debt);
    box.fund = box.fund.add(fund);
    allDebt = allDebt.add(debt);
    allFund = allFund.add(fund);
    emit Enter(msg.sender, count, value, debt, fund);
    adjustAll();
  }

  function skim() external nonReentrant {
    adjustBox(msg.sender);
    Box storage box = boxes[msg.sender];
    uint supply = totalSupply();
    uint wealth = token.balanceOf(address(this));
    uint count = box.debt == 0 ? 0 : box.debt.mul(supply).div(allDebt);
    uint value = box.fund == 0 ? 0 : box.fund.mul(wealth).div(allFund);
    uint maxpo = pricer.getMaxPayout(count);
    if (value > maxpo) {
      uint back = value.sub(maxpo);
      uint less = back.mul(allFund).div(wealth);
      box.fund = box.fund.sub(less);
      allFund = allFund.sub(less);
      token.transfer(msg.sender, back);
      emit Skim(msg.sender, back, less);
    }
  }

  function exit(uint debt) external nonReentrant returns (uint) {
    adjustBox(msg.sender);
    Box storage box = boxes[msg.sender];
    uint count = debt == 0 ? 0 : debt.mul(totalSupply()).div(allDebt);
    uint fund = box.debt == 0 ? box.fund : debt.mul(box.fund).div(box.debt);
    _burn(msg.sender, count);
    box.debt = box.debt.sub(debt);
    allDebt = allDebt.sub(debt);
    box.fund = box.fund.sub(fund);
    uint id = receipts[msg.sender].length;
    receipts[msg.sender].push(Receipt(now + RECEIPT_WAIT_PERIOD, fund, box.fundDecimals));
    emit Exit(msg.sender, id, count, debt, fund);
    return id;
  }

  function claim(uint id) external nonReentrant {
    Receipt storage receipt = receipts[msg.sender][id];
    require(now >= receipt.validAt, '!valid');
    receipt.validAt = uint(-1);
    uint fund = receipt.fund >> (allFundDecimals - receipt.fundDecimals);
    uint value = fund.mul(token.balanceOf(address(this))).div(allFund);
    allFund = allFund.sub(fund);
    token.transfer(msg.sender, value);
    emit Claim(msg.sender, id, value);
  }

  function activate(uint count, uint duration) external nonReentrant returns (uint) {
    uint spending = pricer.getSpending(count, duration);
    _burn(msg.sender, spending);
    _mint(address(1), spending);
    uint id = covers[msg.sender].length;
    covers[msg.sender].push(Cover(count, spending, pricer.getCurrentPrice(), now + duration));
    emit Activate(msg.sender, id, count, duration, spending);
    return id;
  }

  function execute(address owner, uint id)
    external
    nonReentrant
    returns (uint payout, uint bounty)
  {
    Cover storage cover = covers[msg.sender][id];
    uint expiredAt = cover.expiredAt;
    require(expiredAt != 0, '!!executed');
    require(now > expiredAt || msg.sender == owner, '!authorized');
    cover.expiredAt = 0;
    _burn(address(1), cover.spending);
    uint maxPayout = pricer.getMaxPayout(cover.spending);
    uint calPayout = pricer.getPayout(cover.count, cover.startPrice);
    payout = Math.min(maxPayout, calPayout);
    if (msg.sender != owner) {
      uint timeElapsed = Math.min(now - expiredAt, BOUNTY_DECAY_PERIOD);
      uint bountyBps = BOUNTY_BPS_START + ((timeElapsed * BOUNTY_BPS_GROW) / BOUNTY_DECAY_PERIOD);
      bounty = payout.mul(bountyBps).div(BOUNTY_BPS_START + BOUNTY_BPS_GROW);
      payout = payout.sub(bounty);
      token.transfer(msg.sender, bounty);
    }
    token.transfer(owner, payout);
    emit Execute(msg.sender, owner, id, payout, bounty);
  }
}
