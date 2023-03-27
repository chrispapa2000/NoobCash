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

	def __init__(self, port=None):
		# # generate an RSA key
		# keys as numbers
		key = RSA.generate(2048)
		self.public_key_tuple = (key.n, key.e)
		self.private_key_tuple = (key.n, key.e, key.d)


	# def balance():

	# def get_public_key_tuple(self):
	# 	return self.public_key
	
	def get_public_key_tuple(self):
		"""
		returns (n,e) public key tuple
		"""
		return self.public_key_tuple
	
	def get_private_key(self):
		"""
		return a private key object, that can be directly used for signing
		"""
		key = RSA.construct(self.private_key_tuple)
		return key

	def sign(self, port, data):
		# get the key
		key = RSA.construct(self.private_key_tuple)
		
		# signature object
		signer = PKCS1_v1_5.new(key)

		# hash object
		hash_object = SHA.new(data=binascii.a2b_qp(data))

		# sign the hash object
		signature = signer.sign(hash_object)
		return signature

	def verify(self, port, data, signature):
		# get the key
		# f = open(f"personal_keys/public_{port}.pem",'r')
		# key = RSA.import_key(f.read())
		key = RSA.construct(self.public_key_tuple)
		# key = key.public_key()
		
		# signature object
		singer = PKCS1_v1_5.new(key)

		# hash object
		hash_object = SHA.new(data=binascii.a2b_qp(data))

		# sign the hash object
		try:
			singer.verify(hash_object, signature=signature)
			print("Succesful Verification")
		except:
			print("Problem Verifying")

# testing 

def main():
	w = wallet(port=1)
	sig = w.sign(data="Hello World", port=1)
	w.verify(data="Hello World", signature=sig, port=1)

if __name__ == '__main__':
	main()