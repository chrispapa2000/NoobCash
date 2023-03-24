import requests
import block
import node
import transaction
from blockchain import Blockchain
from fileinput import filename
from termcolor import colored

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import os
import pickle
import threading
from flask import Flask, make_response, send_file
import time

# global vars
port = 0
host = ""
number_of_nodes = 5
blockchain = Blockchain()

app = Flask(__name__)
CORS(app)


#--- App Routes ---

def start_everything():
    time.sleep(0.5)

    node.broadcast_participants()
    
    time.sleep(0.5)
    
    node.broadcast_blockchain()
    node.broadcast_initial_transactions()

    node.notify_to_start_mining()
    # time.sleep(0.5)
    # node.start_mining()
    

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
    val = node.create_transaction(sender_address=(my_n,my_e), receiver_address=(int(n), int(e)), private_key=node.wallet.get_private_key(), value=100, do_broadcast=False)
    # init_trans = node.transaction_pool.pop()
    # new_trans = transaction.Transaction(sender_address=None, recipient_address=None, sender_private_key=None, value=None, transaction_inputs=None, init_dict=init_trans.to_dict())
    # l = [init_trans.to_dict()]
    # print("HERE: ", new_trans.to_dict() in l)
    # node.transaction_pool.appendleft(t)
    
    # print("received subscription request")
    # print()
    # print("current ring:", node.ring_dict)
    # print()

    if node.get_id_count() == number_of_nodes - 1:
        t = threading.Thread(target=start_everything, )
        t.start()

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
        f = request.files
        ring = pickle.loads(request.files['ring'].read())
        # print(ring)
       
        # for obj in ringObj['ring']:
        #     obj['public_key'] = obj['public_key'].replace("received_keys", "other_received_keys")

        node.ring_dict = ring
        # print(node.ring_dict)
        for key in node.ring_dict.keys():
            node.UTXOs[key] = []

        return jsonify("OK"), 200
    
@app.route('/broadcast_initial_state', methods=['GET'])
def broadcast_initial_state():
    if node.get_id_count() == number_of_nodes - 1:
        node.broadcast_blockchain()
        # print("broadcasted blockchain")
        node.broadcast_initial_transactions()

        # start mining_thread
        # node.start_mining()
        # t = threading.Thread(target=node.mine)
        node.start_mining()

    return jsonify("OK"), 200

@app.route('/get_initial_blockchain', methods=['POST'])
def route_get_initial_blockchain():
    f = request.files['blockchain_file']
    # f.save(f"tempdir/{f.filename}")
    # node.get_blockchain().from_pickle(f"{f.filename}", basedir="tempdir")
    node.blockchain = pickle.loads(f.read())
    # print(node.get_blockchain().get_chain())
    return jsonify("OK"), 200
    # os.remove(f"tempdir/{f.filename}")
    # node.set_blockchain(blkchain)

@app.route('/get_initial_transactions', methods=['POST'])
def get_initial_transactions():
    f = request.files['initial_transactions_file']
    node.transaction_pool = pickle.loads(f.read())

    for t in node.transaction_pool:
        outputs = t['transaction_outputs']
        for output in outputs:
            receiver = output['receiver_address']
            node.UTXOs[receiver].append(output)

    for t in node.transaction_pool:
        inputs = t['transaction_inputs']
        for input in inputs:
            receiver = input['receiver_address']
            if input in node.UTXOs[receiver]:
                node.UTXOs[receiver].remove(input)
    
    # print("UTXOs:", node.UTXOs)
    print()
    print("--After Initialization--")
    print("Participants:")
    for item in node.ring_dict.values():
        print(item)
        print()
    print("Blockchain:")
    print(node.blockchain.get_chain())
    print()
    print("Transaction Pool:")
    print(node.transaction_pool)
    print("--After Initialization End--")
    print()

    # start mining thread
    node.current_block = block.Block(index=1, previousHash=node.blockchain.get_block_hash(block_index=0))

    # node.start_mining()


    return jsonify("OK"), 200

@app.route('/get_transaction', methods=['POST'])
def get_transaction():
    f = request.files['transaction_file']
    received_transaction = pickle.loads(f.read())
    print(received_transaction)
    node.validate_transaction(received_transaction)
    # print("transaction pool:", node.transaction_pool)
    print()
    print(colored("--Received Transaction", 'blue'))
    print(colored("Current Balances:", 'blue'))
    for item in node.ring_dict.values():
        print(colored(f"id: {item['id']} has {item['balance']}", 'blue'))
    print()
    print(colored("length of UTXOs:", 'blue'))
    print(colored(len(node.UTXOs), 'blue'))
    print()
    print(colored("length of transaction pool:", 'blue'))
    print(colored(len(node.transaction_pool), 'blue'))
    print()
    print(colored(f"current transaction count:{node.transaction_count}", 'blue'))
    print(colored("--Received Transaction End", 'blue'))
    print()

    # decide what to do with the received transaction

    return jsonify("OK"), 200

@app.route('/get_block', methods=['POST'])
def get_block():
    f = request.files['block_file']
    received_block = pickle.loads(f.read())
    # print(received_block)
    # if node.validate_block(the_block=received_block):
    #     node.blockchain.add_block(received_block)
    #     print("inserted new block")
    node.on_new_block_arrival(the_block=received_block)
    # t = threading.Thread(target=node.on_new_block_arrival, args=(received_block,))
    # t.start()

    # decide what to do with the received block
    # block_validation_thread = threading.Thread(target=node.validate_block, args=(received_block,))
    # block_validation_thread.start()
    return jsonify("OK"), 200

# @app.route('/get_chain', methods=['GET'])   #deprecated?
# def get_chain():
#     f = request.files['chain_file']
#     received_chain = pickle.loads(f.read())
#     print(received_chain)

    # decide what to do with the received chain

@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    chain = pickle.dumps(node.blockchain)
    response = make_response(chain)
    response.headers.set('Content-Type', 'application/octet-stream')
    return response
    # chain_file = open('chain.pkl', 'wb')
    # pickle.dump(node.blockchain, file=chain_file)
    # return send_file('chain.pkl')
    # resp = {'blockchain':pickle.dumps(node.blockchain)}
    # return jsonify(resp), 200


@app.route('/get_chain_length', methods=['GET'])
def get_chain_length():
    #f = request.files['length_file']
    #print("got length")
    #received_chain_length = f.read()
    #print(received_chain_length)
    resp = {'length':node.blockchain.get_length()}
    return jsonify(resp), 200

@app.route('/get_transaction_from_cli/<recipient_id>/<amount>', methods=['POST'])
def get_transaction_from_cli(recipient_id, amount):
    recipient_id, amount = int(recipient_id), int(amount)
    # print(f"transfer {amount} noobcash coins to {recipient_id}")
    recipient_key = node.get_pubkey_by_id(recipient_id)
    my_key = node.get_pubkey_by_id(node.id)
    flag = node.create_transaction(sender_address=my_key, receiver_address=recipient_key, private_key=node.wallet.get_private_key(), value=amount, do_broadcast=True)
    
    if not flag:
        # not enough money
        return jsonify("OK"), 200
    
    print()
    print(colored("--Creating transaction--", 'green'))
    print(colored(f"transaction from {node.id} to {recipient_id} with amount={amount}", 'green'))
    print(colored("Current Balances:", 'green'))
    for item in node.ring_dict.values():
        print(colored(f"id: {item['id']} has {item['balance']}", 'green'))
    print(colored("length of UTXOs:", 'green'))
    print(colored(len(node.UTXOs), 'green'))
    print()
    print(colored("length of transaction pool:", 'green'))
    print(colored(len(node.transaction_pool), 'green'))
    print(colored(f"current transaction count:{node.transaction_count}", 'green'))
    print(colored("--Creating transaction End--", 'green'))
    print()
    return jsonify("OK"), 200

@app.route('/start_mining', methods=['GET'])
def route_start_mining():
    node.start_mining()
    return jsonify("OK"), 200

# get all transactions in the blockchain
@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

# @app.route('/test', methods=['GET'])
# def get_test():
#     response = {'test': node.test}
#     return jsonify(response), 200


# run it once for every node
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    #parser.add_argument('--ip', type=str, required=True, help='Node ip address.')
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on.')
    parser.add_argument('-i', '--ip', type=str, help='Node ip address.')
    parser.add_argument('-b', '--bootstrap', default=0, type=int, help='a value of 1 indicates that this is the boostrap node.')
    parser.add_argument('-n', '--number_nodes', default=5, type=int, help='number of total nodes in the blockchain. Only used in bootstrap node.')
    args = parser.parse_args()

    host = args.ip
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


