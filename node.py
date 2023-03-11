import block
import wallet

class node:
	def __init__(self, id=None):
		# self.NBC=100;
		##set

		#self.chain
		#self.current_id_count = 0
		#self.NBCs
		#self.wallet
		#self.id
		#self.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 

		self.current_id_count = 0

		if id:
			self.id = id

		self.ring = []

		self.create_wallet()

	
	def set_id(self, id):
		self.id = id

	def get_id_count(self):
		return self.current_id_count	
	
	def inc_id_count(self):
		self.current_id_count += 1

	def get_node_public_key(self):
		return self.wallet.get_public_key()

	def create_new_block():
		pass

	def create_wallet(self):
		#create a wallet for this node, with a public key and a private key
		self.wallet = wallet.wallet()

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

	def create_transaction(sender, receiver, signature):
		#remember to broadcast it
		pass


	def broadcast_transaction():
		pass


	def validate_transaction():
		#use of signature and NBCs balance
		pass


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



