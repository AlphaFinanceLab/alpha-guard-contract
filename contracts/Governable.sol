pragma solidity 0.6.12;

contract Governable {
  address public governor;
  address public pendingGovernor;

  constructor() public {
    governor = msg.sender;
  }

  modifier onlyGov() {
    require(msg.sender == governor, '!governor');
    _;
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
}
