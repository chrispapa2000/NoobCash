import requests
import block
import node
import transaction
from blockchain import Blockchain
from fileinput import filename


from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


# global vars
port = 0
host = ""
number_of_nodes = 5
blockchain = Blockchain()

app = Flask(__name__)
CORS(app)


#---Initialization Functions---

# function used by non bootstrap nodes to request participation in the blockchain
def request_participation():
    # if you are not the bootstrap server, you request participation from the bootstrap server
    # make a get request
    bootstrap_url = 'http://127.0.0.1:5000'
    with app.app_context():
        files = {'upload_file': open(f"public_{port}.pem",'rb')}
        response = requests.post(f"{bootstrap_url}/participate/{host}/{port}", files=files)
        response_json = response.json()
        print(response_json['id'])
        node.set_id(id=response_json['id'])


def initialize_blockchain():
    # create first transaction
    t0 = transaction.Transaction(sender_address=0, recipient_address=node.get_node_public_key(), sender_private_key=None, value=100*number_of_nodes,
                                 transaction_inputs=[{"transaction_id":0, "receiver_address":0, "amount":100*number_of_nodes}])

    # create genesis block
    genesis_block = block.Block(previousHash=1)

    # add the first transaction to the block
    genesis_block.add_transaction(t0)
    genesis_block.setNonce(0)

    # add the genesis block to the blockchain
    blockchain.add_block(genesis_block)

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


@app.route('/broadcast_participants', methods='GET')
def broadcast_participants():
    if node.get_id_count == number_of_nodes - 1:
        for item in node.ring:
            if item['id'] != node.id:
                url = 'http://'+item["remote_ip"]+':'+item["remote_port"]+'/node_info'
                print(url)
                print(node.ring)
                print()
                response = requests.post(url, json={"hello":1})


@app.route('/node_info/', methods=['POST', 'GET'])
def get_node_info():
    if request.method == 'POST':
        print(request.json['hello'])
        return jsonify("OK"), 200

# # post new transaction to all other nodes
# @app.route('/new_transaction/<trans>', methods=['POST'])
# def post_transaction(trans):
#     if node.validate_transaction(trans):
#         node.add_transaction_to_block(trans)


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
        node = node.node(number_of_nodes=number_of_nodes, id=id, port=port)
        number_of_nodes = args.number_nodes
        # initialize block chain
        initialize_blockchain()


    # executed for all non-bootstrap nodes
    else:
        node = node.node(number_of_nodes=number_of_nodes, port=port)   
        # subscribe to the blockchain, by communicating with the bootstrap node
        request_participation()

    app.run(host=host, port=port)

