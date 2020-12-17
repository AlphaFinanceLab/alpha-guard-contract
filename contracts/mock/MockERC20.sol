pragma solidity 0.6.12;

import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/token/ERC20/ERC20.sol';
import 'OpenZeppelin/openzeppelin-contracts@3.2.0/contracts/access/Ownable.sol';

contract MockERC20 is ERC20, Ownable {
  constructor(string memory name, string memory symbol) public ERC20(name, symbol) {}

  function mint(address to, uint amount) public onlyOwner {
    _mint(to, amount);
  }
}
