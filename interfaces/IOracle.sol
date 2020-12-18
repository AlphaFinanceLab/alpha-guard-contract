pragma solidity 0.6.12;

interface IOracle {
  function getCurrentPrice() external view returns (uint);
}
