import block
import wallet
from transaction import Transaction
from Crypto.Signature import PKCS1_v1_5
import requests
import transaction
from blockchain import Blockchain
import json
import os


class node:
	def __init__(self, number_of_nodes, port, host, id=None):
		# self.NBC=100;
		##set

		#self.chain
		#self.current_id_count = 0
		#self.NBCs
		#self.wallet
		#self.id
		#self.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 
		self.host= host
		self.port = port
		self.number_of_nodes = number_of_nodes

		self.current_id_count = 0

		if id:
			self.id = id

		self.ring = []

		# we store UTXOs for every node 
		self.UTXOs = dict()

		self.create_wallet(port=port)

		self.blockchain = Blockchain()

	#---Initialization Functions---

	# function used by non bootstrap nodes to request participation in the blockchain
	def request_participation(self):
		# if you are not the bootstrap server, you request participation from the bootstrap server
		# make a get request
		bootstrap_url = 'http://127.0.0.1:5000'
		# with app.app_context():
		files = {'upload_file': open(f"personal_keys/public_{self.port}.pem",'rb')}
		response = requests.post(f"{bootstrap_url}/participate/{self.host}/{self.port}", files=files)
		response_json = response.json()
		print(response_json['id'])
		self.set_id(id=response_json['id'])

	# function that initializes the blockchain in the bootstrap node
	def initialize_blockchain(self):
		# create first transaction
		t0 = transaction.Transaction(sender_address=0, recipient_address=self.get_node_public_key(), sender_private_key=None, value=100*self.number_of_nodes,
									transaction_inputs=[{"transaction_id":0, "receiver_address":0, "amount":100*self.number_of_nodes}])

		# create genesis block
		genesis_block = block.Block(previousHash=1,index=0)

		# add the first transaction to the block
		genesis_block.add_transaction(t0)
		genesis_block.setNonce(0)

		# add the genesis block to the blockchain
		self.blockchain.add_block(genesis_block)

	# function that broadcast info gathered by the bootstrap node to all other nodes
	def broadcast_participants(self):
		# get all pub key files names 
		filenames = [item for item in os.listdir('received_keys') if item.startswith("public")]
		files = dict()
		for item in filenames:
			files[item] = open(f"received_keys/{item}", 'rb')
		files["ring"]=json.dumps({"ring":self.get_ring()}) 

		# files = {'file1': open('report.xls', 'rb'), 'file2': open('otherthing.txt', 'rb')}
		for other_node in self.get_ring():
			if other_node['id'] != self.id:
				url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_participants_info'
				response = requests.post(url, files=files)
	
	# function that broadcasts the initial blockhain from the bootstrap node to the other nodes 
	def braodcast_blockchain(self):
		for other_node in self.get_ring():
			url = 'http://'+other_node["remote_ip"]+':'+other_node["remote_port"]+'/get_initial_blockchain'
			json = {"blockchain":self.get_blockchain()}



	#---Normal Class Functions---
	def set_id(self, id):
		self.id = id

	def get_id_count(self):
		return self.current_id_count	
	
	def inc_id_count(self):
		self.current_id_count += 1

	def get_node_public_key(self):
		return self.wallet.get_public_key()
	
	def get_UTXOs(self, id):
		return self.UTXOs[id]
	
	def set_UTXOs(self, id, nbcList):
		self.UTXOs[id] = nbcList

	def get_ring(self):
		return self.ring
	
	def set_ring(self, ring):
		self.ring = ring

	def get_blockchain(self):
		return self.blockchain()
	
	def create_new_block(self, previousHash):
		self.current_block = block.Block(previousHash=previousHash)

	def create_wallet(self, port):
		#create a wallet for this node, with a public key and a private key
		self.wallet = wallet.wallet(port=port)

	def register_node_to_ring(self, id, public_key, remote_ip, remote_port, balance=0):
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		new_node = {
			'id':id,
			'public_key':public_key,
			'remote_ip':remote_ip,
			'remote_port':remote_port,
			'balance':balance
		} 
		self.ring.append(new_node)
		pass

	# def create_transaction(sender_address, receiver_address, signature):
	def create_transaction(self, sender_address, receiver_address, private_key,value):
		#remember to broadcast it
		
		# find UTXOs to send
		myUTXOs = self.get_UTXOs(sender_address)
		total = value
		transaction_inputs = []

		for item in myUTXOs:
			total -= item["amount"]
			transaction_inputs.append(item)
			if total <= 0:
				break
		
		myUTXOs = list(set(myUTXOs).difference(set(transaction_inputs)))
		# update your UTXOs
		self.set_UTXOs(sender_address, myUTXOs)

		# initialize transaction
		trans = Transaction(sender_address=sender_address, recipient_address=receiver_address, sender_private_key=private_key, value=value, 
		      transaction_inputs=transaction_inputs)
		
		# add to block
		self.current_block.add_transaction(trans)

		# broadcast

		

	def broadcast_transaction():
		pass


	def validate_transaction(self, trans: Transaction):
		#use of signature and NBCs balance
		# check signature
		trans_dict = trans.to_dict()
		# signer object
		singer = PKCS1_v1_5.new(trans_dict['sender_address'])
		# hash object
		hash_object = trans_dict["transaction_id"]
		#signature
		signature = trans_dict["signature"]

		# verify
		try:
			singer.verify(hash_object, signature=signature)
			print("Succesful Verification")
		except:
			print("Problem Verifying")
		
		# check NBCs balance


	def add_transaction_to_block():
		#if enough transactions  mine
		pass



	def mine_block():
		pass


	def broadcast_block():
		pass


		

	# def valid_proof(.., difficulty=MINING_DIFFICULTY):
	# 	pass




	# #concencus functions

	# def valid_chain(self, chain):
	# 	#check for the longer chain accroose all nodes
	# 	pass


	# def resolve_conflicts(self):
	# 	#resolve correct chain
	# 	pass



