
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
		self.timestamp = time.now()
		self.listOfTransactions = []

	
	def myHash(self):
		#calculate self.hash

		self.hash = 1 # to be changed 


	def add_transaction(self, trnsaction, blckchain):
		#add a transaction to the block
		self.listOfTransactions.append(trnsaction)