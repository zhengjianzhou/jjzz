import hashlib
import json
import requests
from time import time
from urlparse import urlparse
from uuid import uuid4
from flask import Flask, jsonify, request

# Helper functions
def hash(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def proof_of_work(last_proof):
    proof = 0
    while valid_proof(last_proof, proof) is False:
        proof += 1
    return proof

def valid_proof(last_proof, proof):
    guess = '{0}{1}'.format(last_proof, proof).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"


class BlockChain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        self.nodes.add(urlparse(address).netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        for current_index in range(1, len(chain)):
            block = chain[current_index]
            
            if block['previous_hash'] != hash(last_block): return False
            if not valid_proof(last_block['proof'], block['proof']): return False

            last_block = block

        return True

    def resolve_conflicts(self):
        neighbours, new_chain, max_length = self.nodes, None, len(self.chain)

        for node in neighbours:
            response = requests.get('http://{0}/chain'.format(node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Validate and get the longer chain
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        block = {
            'index'         : len(self.chain) + 1,
            'timestamp'     : time(),
            'transactions'  : self.current_transactions,
            'proof'         : proof,
            'previous_hash' : previous_hash or hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender'    : sender,
            'recipient' : recipient,
            'amount'    : amount,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
BlockChain = BlockChain()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = BlockChain.last_block
    last_proof = last_block['proof']
    proof = proof_of_work(last_proof)

    BlockChain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = hash(last_block)
    block = BlockChain.new_block(proof, previous_hash)

    response = {
        'message'       : "New Block Forged",
        'index'         : block['index'],
        'transactions'  : block['transactions'],
        'proof'         : block['proof'],
        'previous_hash' : block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        return 'Missing values', 400

    index = BlockChain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': 'Transaction will be added to Block {0}'.format(index)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain'     : BlockChain.chain,
        'length'    : len(BlockChain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        BlockChain.register_node(node)

    response = {
        'message'       : 'New nodes have been added',
        'all_nodes'     : list(BlockChain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = BlockChain.resolve_conflicts()

    if replaced:
        response = {
            'message'   : 'This chain was replaced',
            'new_chain' : BlockChain.chain
        }
    else:
        response = {
            'message'   : 'This chain is authoritative',
            'chain'     : BlockChain.chain
        }

    return jsonify(response), 200


app.run(host='localhost', port=5000)
