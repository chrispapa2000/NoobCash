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

	def __init__(self, port):
		# generate an RSA key
		# export private key
		key = RSA.generate(2048)
		private_key = key.export_key()
		file_out = open(f"personal_keys/private_{port}.pem", 'wb')
		file_out.write(private_key)
		file_out.close()

		# export public key
		public_key = key.publickey().export_key()
		file_out = open(f"personal_keys/public_{port}.pem", "wb")
		file_out.write(public_key)
		file_out.close()
		
		# keys as class attibutes
		self.public_key = key.public_key()
		self.private_key = key

		#self_address
		#self.transactions

	# def balance():

	def get_public_key(self):
		return self.public_key

	def sign(self, port, data):
		# get the key
		f = open(f"personal_keys/private_{port}.pem",'r')
		key = RSA.import_key(f.read())
		
		# signature object
		signer = PKCS1_v1_5.new(key)

		# hash object
		hash_object = SHA.new(data=binascii.a2b_qp(data))

		# sign the hash object
		signature = signer.sign(hash_object)
		return signature

	def verify(self, port, data, signature):
		# get the key
		f = open(f"personal_keys/public_{port}.pem",'r')
		key = RSA.import_key(f.read())
		# key = key.public_key()
		
		# signature object
		singer = PKCS1_v1_5.new(key)

		# hash object
		hash_object = SHA.new(data=binascii.a2b_qp(data)).hexdigest()

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