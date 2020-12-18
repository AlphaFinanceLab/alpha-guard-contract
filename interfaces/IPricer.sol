pragma solidity 0.6.12;

import './IOracle.sol';

interface IPricer is IOracle {
  function getSpending(uint count, uint duration) external view returns (uint);

  function getMaxPayout(uint spending) external view returns (uint);

  function getPayout(uint count, uint startPrice) external view returns (uint);
}
