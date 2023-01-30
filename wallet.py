import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

class wallet:

	def __init__(self):
		# generate an RSA key
		key = RSA.generate(2048)

		self.public_key = key.public_key()
		self.private_key = key

		#self_address
		#self.transactions

	# def balance():



# testing 

def main():
	w = wallet()

if __name__ == '__main__':
	main()