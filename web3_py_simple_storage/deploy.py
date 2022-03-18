from solcx import compile_standard, install_solc
import json

from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


# reading the solidity file
with open("./simple_storage.sol", "r") as file:
    simple_storage_file = file.read()
    print(simple_storage_file)

# installing solc version
print("Installing...")
install_solc("0.6.0")


# complile our solidity code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"simple_storage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

# print(compiled_sol)

# output to a file
with open("compile_code.json", "w") as file:
    json.dump(compiled_sol, file)


"""Deploying in python"""

# get bytecode from the output file
bytecode = compiled_sol["contracts"]["simple_storage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi from the output file
abi = json.loads(
    compiled_sol["contracts"]["simple_storage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]


""" Connecting to Ganache """

# connecting to the http link
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))

# chain id / network id
chain_id = 1337

# an address
my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"

# private key
private_key = os.getenv("PRIVATE_KEY")
# always add "0x" to the private key


""" Create the contract in python"""
simpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)


# 1. Build the transaction
transaction = simpleStorage.constructor().buildTransaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": my_address,
    "nonce": nonce
})

# 2. Sign the transaction
signed_transaction = w3.eth.account.sign_transaction(
    transaction, private_key=private_key)

print("Deploying Contract!")

# 3. Send the transaction to the blockchain
transaction_hash = w3.eth.send_raw_transaction(
    signed_transaction.rawTransaction)

# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")

transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)

print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")


""" Working with deployed contract """
# we need the address and the abi to work with the deployed contract

simple_storage = w3.eth.contract(
    address=transaction_receipt.contractAddress, abi=abi)

# call -> stimulate making the call and getting the return value
# transact -> actually make a state change

# the initial value of favorite number
print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")

# 1. Build the transaction
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": my_address,
    "nonce": nonce + 1
})

# 2. Sign the transaction
signed_store_transaction = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key)


# Send the transaction
store_transaction_hash = w3.eth.send_raw_transaction(
    signed_store_transaction.rawTransaction)
print("Updating stored Value...")

store_transaction_receipt = w3.eth.wait_for_transaction_receipt(
    store_transaction_hash)

print(f"Updated value: {simple_storage.functions.retrieve().call()}")
