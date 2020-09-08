from functools import reduce
from utility.hash_util import hash_block
import json
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet

# The reward we give to miners (for creating a new block)
MINING_REWARD = 10

print(__name__)


class Blockchain:
    def __init__(self, hosting_node_id):
        # Our starting block for the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # Initializing our (empty) blockchain list
        self.chain = [genesis_block]
        # Unhandled transactions
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        """Initialize blockchain + open transactions data from a file."""
        try:
            with open('blockchain.txt', mode='r') as f:
                # file_content = pickle.loads(f.read())
                file_content = f.readlines()

                # blockchain_list = file_content['chain']
                # open_transactions = file_content['ot']
                blockchain_list = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain_list:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in
                                    block['transactions']]
                    updated_block = Block(block['index'],
                                          block['previous_hash'],
                                          converted_tx,
                                          block['proof'],
                                          block['timestamp'])
                    updated_blockchain.append(updated_block)
                    self.chain = updated_blockchain
                    open_transactions = json.loads(file_content[1])
                    updated_transactions = []
                    for tx in open_transactions:
                        updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                        updated_transactions.append(updated_transaction)
                    self.open_transactions = updated_transactions
        except (IOError, IndexError):
            print('Handled exception')
            pass
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index,
                                                                     block_el.previous_hash,
                                                                     [tx.__dict__ for tx in block_el.transactions],
                                                                     block_el.proof,
                                                                     block_el.timestamp) for block_el in
                                                               self.__chain]]
                # Use Json as example
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                # Use Pickle
                # save_data = {
                #     'chain': blockchain_list,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Try different PoW numbers and return the first valid one
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        """Generate a proof of work for the open transactions, the hash of the previous block and a random number (
        which is guessed until it fits). """
        if self.hosting_node == None:
            return None
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in
                     self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                             tx_sender, 0)
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                        self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                                 tx_recipient, 0)
        # # Old Logic replace by lambda function
        # amount_received: float = 0
        # for tx in tx_recipient:
        #     if len(tx) > 0:
        #         amount_received += tx[0]
        # Return the total balanced that we have in the end
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """
        This Function return the latest blockchain value from the list
        :return: Latest Value
        """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """

        This function accepts two arguments

        :param recipient: The recipient of the coins
        :param sender: The sender of the coins
        :param amount: The amount of the coins sent with the transaction (default = 1.0)
        :return:
        Returning the last value of the current blockchain
        """
        if self.hosting_node == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """
        Create a new block and add open transactions to it
        :return:
        """
        if self.hosting_node is None:
            return None

        # Fetch the currently last block of the blockchain
        last_block = self.__chain[-1]
        # Hash the last block (to be able to compare it to the stored hash value)
        hashed_block = hash_block(last_block)
        # print(hashed_block)
        proof = self.proof_of_work()

        # Miners should be reward , so we create a reward transaction
        reward_transaction = Transaction('MINING', self.hosting_node, '', MINING_REWARD)
        # Copy transaction instead of manipulating the original open_transactions
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)

        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)

        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block
