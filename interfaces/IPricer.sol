pragma solidity 0.6.12;

interface IPricer {
  function getCurrentPrice() external view returns (uint);

  function getSpending(uint count, uint duration) external view returns (uint);

  function getMaxPayout(uint spending) external view returns (uint);

  function getPayout(uint count, uint startPrice) external view returns (uint);
}
