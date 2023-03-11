
# import blockchain
import transaction
import time




class Block:
	def __init__(self, previousHash):
		##set
		#self.previousHash
		#self.timestamp
		#self.hash
		#self.nonce
		#self.listOfTransactions
		self.previousHash = previousHash
		self.timestamp = time.time()
		self.listOfTransactions = []

	
	def myHash(self):
		#calculate self.hash
		self.hash = 1 # to be changed 

	def setNonce(self, nonce):
		self.nonce = nonce
		
	def add_transaction(self, trans, blkchain=None):
		#add a transaction to the block
		self.listOfTransactions.append(trans)