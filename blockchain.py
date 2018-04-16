import hashlib
import json

from time import time
from uuid import uuid4


class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # first block in chain
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Creates new block for chain
        :param proof: <int> proof given by POF
        :param previous_hash: <str> hash of previous block
        :return: <dict> new block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'hash': previous_hash or self.hash(self.chain[-1])
        }

        # reset current transactions after creation of block
        self.current_transactions = []

        self.chain.append(block)
        return block


    def new_transaction(self, sender, recip, amount):
        """
        Creates new transaction to be added to next Block
        :param sender: <str> Sender address
        :param recip: <str> Recipient address
        :param amount: <int> Amount
        :return: <int> Index of block to be added to
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recip,
            'amount': amount
        })

        return self.last_block['index'] + 1


    def proof_of_work(self):
        pass

    @staticmethod
    def hash(block):
        """
        Create SHA-256 hash of block
        :param block: <dict> block
        :return: <str> hash
        """

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        return self.chain[-1]