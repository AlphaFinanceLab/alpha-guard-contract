pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/SafeMath.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/Math.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol';
import './Governable.sol';
import '../interfaces/IPricer.sol';

library ILMath {
  function sqrt(uint x) internal pure returns (uint y) {
    uint z = (x + 1) / 2;
    y = x;
    while (z < y) {
      y = z;
      z = (x / z + z) / 2;
    }
  }
}

contract UniswapILPricer is Governable, IPricer {
  using SafeMath for uint;

  IOracle public oracle;
  uint public maxPayoutPerSpending;
  mapping(uint => uint) public durationToSpending;

  constructor(
    IOracle _oracle,
    uint _maxPayoutPerSpending,
    uint[] memory durationList,
    uint[] memory spendingList
  ) public {
    oracle = _oracle;
    maxPayoutPerSpending = _maxPayoutPerSpending;
    require(durationList.length == spendingList.length, 'inconsistent length');
    for (uint idx = 0; idx < durationList.length; idx++) {
      durationToSpending[durationList[idx]] = spendingList[idx];
    }
  }

  function setOracle(IOracle _oracle) external onlyGov {
    oracle = _oracle;
  }

  function setMaxPayoutPerSpending(uint _maxPayoutPerSpending) external onlyGov {
    maxPayoutPerSpending = _maxPayoutPerSpending;
  }

  function setDurationToSpending(uint[] memory durationList, uint[] memory spendingList)
    external
    onlyGov
  {
    require(durationList.length == spendingList.length, 'inconsistent length');
    for (uint idx = 0; idx < durationList.length; idx++) {
      durationToSpending[durationList[idx]] = spendingList[idx];
    }
  }

  function getCurrentPrice() external view override returns (uint) {
    return oracle.getCurrentPrice();
  }

  function getSpending(uint count, uint duration) external view override returns (uint) {
    uint spendingPerUnit = durationToSpending[duration];
    require(spendingPerUnit != 0, 'invalid duration');
    return count.mul(spendingPerUnit).div(1e18);
  }

  function getMaxPayout(uint spending) external view override returns (uint) {
    return maxPayoutPerSpending.mul(spending).div(1e18);
  }

  function getPayout(uint count, uint startPrice) external view override returns (uint) {
    uint sqrtStart = ILMath.sqrt(startPrice);
    uint sqrtEnd = ILMath.sqrt(oracle.getCurrentPrice());
    uint diffSqrt = sqrtStart > sqrtEnd ? sqrtStart - sqrtEnd : sqrtEnd - sqrtStart;
    return count.mul(diffSqrt).div(sqrtStart).mul(diffSqrt).div(sqrtEnd).div(2);
  }
}
