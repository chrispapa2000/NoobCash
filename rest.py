# import blockchain
# import wallet
import requests
import block
import node
import transaction
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# global vars
port = 0
host = ""
number_of_nodes = 5

app = Flask(__name__)
CORS(app)
# blockchain = Blockchain()


#---Initialization Functions---

# function used by non bootstrap nodes to request participation in the blockchain
def request_participation():
    # if you are not the bootstrap server, you request participation from the bootstrap server
    # make a get request
    bootstrap_url = 'http://127.0.0.1:5000'
    public_key = 1
    with app.app_context():
        response = requests.get(f"{bootstrap_url}/participate/{public_key}/{host}/{port}")
        response_json = response.json()
        print(response_json['id'])
        node.set_id(id=response_json['id'])

# function 
def broadcast_node_info():
    pass

def initialize_blockchain():
    # create first transaction
    t0 = transaction.Transaction(sender_address=0, recipient_address=node.get_node_public_key(), value=100*number_of_nodes)

    # create genesis block
    genesis_block = block.Block(previousHash=1)

    # add the first transaction to the block
    genesis_block.add_transaction(t0)
    genesis_block.setNonce(0)

    # 


#--- App Routes ---

# route called in the bootstrap node to allow other nodes to participate
@app.route('/participate/<public_key>/<remote_ip>/<remote_port>', methods=['GET'])
def participate(public_key, remote_ip, remote_port):
    node.inc_id_count()
    id = node.get_id_count()
    node.register_node_to_ring(id, public_key, remote_ip, remote_port, balance=0)
    resp = {"id":node.current_id_count}

    print("_____________________________")
    print("received subscription request")
    print("current ring:", node.ring)
    print("_____________________________")


    # if we have reached the desird number of participants inform all nodes
    if node.get_id_count() == number_of_nodes - 1:
        broadcast_node_info()

    return jsonify(resp), 200


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
        node = node.node(id=id)
        number_of_nodes = args.number_nodes
        # initialize block chain
        initialize_blockchain()


    # executed for all non-bootstrap nodes
    else:
        node = node.node()   
        # subscribe to the blockchain, by communicating with the bootstrap node
        request_participation()

    app.run(host=host, port=port)

