import requests
import block
import node
import transaction
from blockchain import Blockchain
from fileinput import filename


from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os
import pickle
import threading

# global vars
port = 0
host = ""
number_of_nodes = 5
blockchain = Blockchain()

app = Flask(__name__)
CORS(app)


#--- App Routes ---

# route called in the bootstrap node to allow other nodes to participate
@app.route('/participate/<remote_ip>/<remote_port>/<n>/<e>', methods=['POST'])
def participate(remote_ip, remote_port, n, e):
    # detach pub key file and save it
    # f = request.files['upload_file']
    # f.save(f"received_keys/{f.filename}")
    
    # get new node id
    node.inc_id_count()
    id = node.get_id_count()

    # save new node's data
    node.register_node_to_ring(id, (int(n),int(e)), remote_ip, remote_port, balance=0)
    node.UTXOs[(int(n),int(e))]=[]
    resp = {"id":node.current_id_count}
    (my_n,my_e) = node.get_my_public_key_tuple()

    t = node.create_transaction(sender_address=(my_n,my_e), receiver_address=(int(n), int(e)), private_key=node.wallet.get_private_key(), value=100, do_broadcast=False)
    node.transaction_pool.appendleft(t)
    
    print("received subscription request")
    print()
    print("current ring:", node.ring_dict)
    print()
    print(f"current transaction pool: {node.transaction_pool}")
    for (a,b) in node.UTXOs.items():
        print(f"key: {a}")
        print(b)
        print()
    print("==============================================================================================================")

    # return response
    return jsonify(resp), 200


@app.route('/broadcast_participants', methods=['GET'])
def route_broadcast_participants():
    if node.get_id_count() == number_of_nodes - 1:
        node.broadcast_participants()
    return jsonify("OK"), 200

@app.route('/get_participants_info/', methods=['POST', 'GET'])
def get_participants_info():
    if request.method == 'POST':    
        # print(request.json['ring'])
        # print(request.files)
        f = request.files
        print(f)
        ring = pickle.loads(request.files['ring'].read())
        print(ring)
       
        # for obj in ringObj['ring']:
        #     obj['public_key'] = obj['public_key'].replace("received_keys", "other_received_keys")

        node.ring_dict = ring
        print(node.ring_dict)
        print("==============================================================================================================")
        # node.ring_to_dict()
        return jsonify("OK"), 200
    
@app.route('/broadcast_initial_state', methods=['GET'])
def broadcast_initial_state():
    if node.get_id_count() == number_of_nodes - 1:
        node.broadcast_blockchain()
        print("broadcasted blockchain")
        node.broadcast_initial_transactions()

    return jsonify("OK"), 200

@app.route('/get_initial_blockchain', methods=['POST'])
def route_get_initial_blockchain():
    f = request.files['blockchain_file']
    # f.save(f"tempdir/{f.filename}")
    # node.get_blockchain().from_pickle(f"{f.filename}", basedir="tempdir")
    node.blockchain = pickle.loads(f.read())
    print(node.get_blockchain().get_chain())
    print("==============================================================================================================")
    return jsonify("OK"), 200
    # os.remove(f"tempdir/{f.filename}")
    # node.set_blockchain(blkchain)

@app.route('/get_initial_transactions', methods=['POST'])
def get_initial_transactions():
    f = request.files['initial_transactions_file']
    node.transaction_pool = pickle.loads(f.read())
    for t in node.transaction_pool:
        print(t.sender_address) 
    return jsonify("OK"), 200

@app.route('/get_transaction', methods=['POST'])
def get_transaction():
    f = request.files['transaction_file']
    received_transaction = pickle.loads(f.read())
    print(received_transaction)

    # decide what to do with the received transaction

@app.route('/get_block', methods=['POST'])
def get_block():
    f = request.files['block_file']
    received_block = pickle.loads(f.read())
    print(received_block)

    # decide what to do with the received block
    block_validation_thread = threading.Thread(target=node.validate_block, args=(received_block,))
    block_validation_thread.start()
    return jsonify("OK"), 200

@app.route('/get_chain', methods=['POST'])
def get_chain():
    f = request.files['chain_file']
    received_chain = pickle.loadds(f.read())
    print(received_chain)

    # decide what to do with the received chain


    


# get all transactions in the blockchain
@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200


# run it once for every node
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on.')
    parser.add_argument('-b', '--bootstrap', default=0, type=int, help='a value of 1 indicates that this is the boostrap node.')
    parser.add_argument('-n', '--number_nodes', default=5, type=int, help='number of total nodes in the blockchain. Only used in bootstrap node.')
    args = parser.parse_args()
    port = args.port
    host = '127.0.0.1'

    # only executed for bootstrap node
    if args.bootstrap == 1:
        number_of_nodes = args.number_nodes
        node = node.node(number_of_nodes=number_of_nodes, host=host, port=port, id=0)
        # initialize block chain
        node.initialize_blockchain()
        node.register_node_to_ring(id=0, public_key=node.get_my_public_key_tuple(), remote_ip=host, remote_port=str(port), balance=100*number_of_nodes)


    # executed for all non-bootstrap nodes
    else:
        node = node.node(number_of_nodes=number_of_nodes, host=host, port=port)   
        # subscribe to the blockchain, by communicating with the bootstrap node
        node.request_participation()

    app.run(host=host, port=port)

