import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

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


    def proof_of_work(self, last_proof):
        """
        Simple proof of work algorithm
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0

        while self.validate_proof(last_proof, proof) is False:
            proof += 1


        return proof


    @staticmethod
    def validate_proof(last_proof, proof):
        """
        Validates proof
        :param last_proof: <int> previous proof
        :param proof: <int> current proof 
        :return: True if correct, False otherwise
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0010"

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


app = Flask(__name__)

# generate unique address
node_identifier = str(uuid4()).replace('-','')

#start blockchain
blockchain = BlockChain

@app.route('/mine', method=['GET'])
def mine():
    return "Mining New Block"

@app.route('/transactions/new', method=['POST'])
def new_transaction():
    return "New Transaction occurring"

@app.route('/chain', method=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)