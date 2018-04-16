import hashlib
import json

from time import time
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, request

class BlockChain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.nodes = set()

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

    def register_nodes(self, new_node):
        """
        Adds new node to set
        :param new_node: <str> address of new node
        :return:
        """
        url = urlparse(new_node)
        self.nodes.add(url)

    def valid_chain(self, chain):
        """
        Determine if blockchain is valid (consensus)
        :param chain: <list> blockchain
        :return: <bool> True if true, else False
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}\n{block}\n------------')

            # check that hash of block is correct
            if block['previous_hash'] is not self.hash(last_block):
                return False

            # check that proof of work is correct
            if not self.validate_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Consensus Algorithm that repplaces chain with longest in network
        :return: <bool> True if chain, replaced, False otherwise
        """

        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)

        # compare chains in network ot ours
        for node in neighbors:
            response = request.get(f'http://{node}/chain')


            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # compare length of chains
                if length > max_length:
                    max_length = length
                    new_chain = chain

        # replace chain if new, valid chain found
        if new_chain:
            self.chain = new_chain
            return True

        return False

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
blockchain = BlockChain()

@app.route('/mine', method=['GET'])
def mine():
    # proof of work algorithm being run
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #reward given for finding proof, "0" means node has mined coined
    blockchain.new_transaction(
        sender="0",
        recip=node_identifier,
        amount=1
    )

    # add block to blockchain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Created",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previoush_hash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', method=['POST'])
def new_transaction():
    values = request.get_json()

    # check for fields in data
    required = ['sender','recipient','amount']
    if not all(k in values for k in required):
        return 'Missing input', 400

    index = blockchain.new_transaction(values['sender', values['recipient'], values['amount']])

    response = {'message': f'Transaction added at {index}'}

    return jsonify(response), 201

@app.route('/chain', method=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response)

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')

    if nodes is None:
        return "Error: No nodes", 400

    for node in nodes:
        blockchain.register_nodes(node)

    response = {
        'message': 'New Node added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/nodes/resolve', method=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'BlockChain replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'BlockChain correct',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)