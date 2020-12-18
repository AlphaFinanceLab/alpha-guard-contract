pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/SafeMath.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/math/Math.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol';
import './Governable.sol';
import '../interfaces/IPricer.sol';

contract SimplePricer is Governable, IPricer {
  using SafeMath for uint;

  uint public price;
  address public relayer;

  constructor(uint _price) public {
    price = _price;
    relayer = msg.sender;
  }

  function setRelayer(address _relayer) external onlyGov {
    relayer = _relayer;
  }

  function setPrice(uint _price) external {
    require(msg.sender == relayer || msg.sender == governor, '!relayer');
    price = _price;
  }

  function getCurrentPrice() external view override returns (uint) {
    return price;
  }

  function getSpending(uint count, uint duration) external view override returns (uint) {
    return count.add(count.mul(duration).div(1 days));
  }

  function getMaxPayout(uint spending) external view override returns (uint) {
    return spending;
  }

  function getPayout(uint count, uint startPrice) external view override returns (uint) {
    uint lower = Math.min(startPrice, price);
    uint upper = Math.max(startPrice, price);
    return count - count.mul(lower).div(upper);
  }
}
