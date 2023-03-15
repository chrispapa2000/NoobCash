import requests
import block
import node
import transaction
from blockchain import Blockchain
from fileinput import filename


from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json


# global vars
port = 0
host = ""
number_of_nodes = 5
blockchain = Blockchain()

app = Flask(__name__)
CORS(app)


#--- App Routes ---

# route called in the bootstrap node to allow other nodes to participate
@app.route('/participate/<remote_ip>/<remote_port>', methods=['POST'])
def participate(remote_ip, remote_port):
    # detach pub key file and save it
    f = request.files['upload_file']
    f.save(f"received_keys/{f.filename}")
    
    # get new node id
    node.inc_id_count()
    id = node.get_id_count()

    # save new node's data
    node.register_node_to_ring(id, f"received_keys/{f.filename}", remote_ip, remote_port, balance=0)
    resp = {"id":node.current_id_count}

    print("_____________________________")
    print("received subscription request")
    print("current ring:", node.ring)
    print("_____________________________")

    # return response
    return jsonify(resp), 200


@app.route('/broadcast_participants', methods=['GET'])
def route_broadcast_participants():
    if node.get_id_count() == number_of_nodes - 1:
        node.broadcast_participants()
    return jsonify("OK"), 200

@app.route('/broadcast_blockchain', methods=['GET'])
def route_broadcast_blockchain():
    if node.get_id_count == number_of_nodes - 1:
        pass


@app.route('/get_participants_info/', methods=['POST', 'GET'])
def get_participants_info():
    if request.method == 'POST':
        # print(request.json['ring'])
        # print(request.files)
        f = request.files
        for filename in f:
            if filename != 'ring':
                f[filename].save(f"other_received_keys/{filename}")
        ringObj = json.loads(request.files['ring'].read())
        node.set_ring(ringObj['ring'])
        print(node.get_ring())
        return jsonify("OK"), 200

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
        node = node.node(number_of_nodes=number_of_nodes, host=host, port=port, id=id)
        number_of_nodes = args.number_nodes
        # initialize block chain
        node.initialize_blockchain()


    # executed for all non-bootstrap nodes
    else:
        node = node.node(number_of_nodes=number_of_nodes, host=host, port=port)   
        # subscribe to the blockchain, by communicating with the bootstrap node
        node.request_participation()

    app.run(host=host, port=port)

