
# import blockchain
import transaction
import time
import pickle
# import json
# from Crypto.Hash import SHA256


class Block:
	def __init__(self, index, previousHash, capacity=5, ):
		##set
		#self.previousHash
		#self.timestamp
		#self.hash
		#self.nonce
		#self.listOfTransactions
		self.index = index
		self.previousHash = previousHash
		self.capacity = capacity
		self.timestamp = time.time()
		self.listOfTransactions = []
		#self.nonce = None
		#self.current_hash = None

	def to_dict(self):
		d = {
			"index": self.index,
			"previousHash": self.previousHash,
			"timestamp": self.timestamp,
			"capacity": self.capacity,
			"listOfTransactions": self.listOfTransactions#,
			#"nonce": self.nonce,
			#"current_hash": self.current_hash
		}
		return d

	def myHash(self):
		#calculate self.hash
		#block_list = [self.timestamp, [tr.transaction_id for tr in self.listOfTransactions], self.nonce, self.previousHash]
		#tmp = json.dumps(block_list.to_dict())
		#self.hash = SHA256.new(tmp.encode("ISO-8859-2")).hexdigest()
		self.hash = 1 # to be changed 

	#two blocks are equal if current hash is equal
	def __eq__(self, other):
		return self.current_hash == other.current_hash
	
	def setNonce(self, nonce):
		self.nonce = nonce # this maybe has to go on init too? 
		
	def add_transaction(self, trans: transaction.Transaction, blkchain=None):
		if self.is_filled():
			raise Exception("Block is filled. Adding transaction would exceed capacity.")

        #add a transaction to the block
		self.listOfTransactions.append(trans.to_dict())

	def is_filled(self):
		return len(self.listOfTransactions) >= self.capacity
	
	def to_pickle(self, filename, basedir='pickles'):
		with open(f"{basedir}/{filename}", 'wb') as f:  # open a text file
			pickle.dump(self, f) # serialize the class 

	def from_pickle(self, filename, basedir='pickles'):
		# open pickle file and read it
		with open(f"{basedir}/{filename}", 'rb') as f:
			temp = pickle.load(f)
		
		# transfer the data to current object 
		self.index = temp.index
		self.previousHash = temp.previousHash
		self.capacity = temp.capacity
		self.timestamp = temp.capacity
		self.listOfTransactions = temp.listOfTransactions
		self.hash = temp.hash
		self.nonce = temp.nonce
		
		# # delete .pickle file
		# os.remove(filename)

		
