
# import blockchain
import transaction
import time




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

	def to_dict(self):
		d = {
			"index": self.index,
			"previousHash": self.previousHash,
			"timestamp": self.timestamp,
			"capacity": self.capacity,
			"listOfTransactions": self.listOfTransactions
		}
		
	def myHash(self):
		#calculate self.hash
		self.hash = 1 # to be changed 

	def setNonce(self, nonce):
		self.nonce = nonce
		
	def add_transaction(self, trans: transaction.Transaction, blkchain=None):
		if self.is_filled():
			raise Exception("Block is filled. Adding transaction would exceed capacity.")

        #add a transaction to the block
		self.listOfTransactions.append(trans.to_dict())

	def is_filled(self):
		return len(self.listOfTransactions) >= self.capacity
