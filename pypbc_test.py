#! /usr/bin/env python3

"""
test.py
Written by Geremy Condra
Licensed under GPLv3
Released 11 October 2009
"""

import unittest

from pypbc import *

stored_params = """type a
q 8780710799663312522437781984754049815806883199414208211028653399266475630880222957078625179422662221423155858769582317459277713367317481324925129998224791
h 12016012264891146079388821366740534204802954401251311822919615131047207289359704531102844802183906537786776
r 730750818665451621361119245571504901405976559617
exp2 159
exp1 107
sign1 1
sign0 1
"""

from pypbc import *
import hashlib
import time
from random import sample
import numpy as np

Hash1 = hashlib.sha256
Hash2 = hashlib.sha256
params = Parameters(qbits=512, rbits=160)  # type a
pairing = Pairing(params)
# 返回公共参数，PEKS是对称双线性对，G1=G2,二者的生成元是一样的，G2同样可以替换为G1
qbits = 512
rbits = 160

g = Element.random(pairing, G1)
sk = Element.random(pairing, Zr)
pk = Element(pairing, G1, g ** sk)
U = Element.random(pairing, G1)

x1 = Element.random(pairing, G1)
x2 = Element.random(pairing, Zr)

z = Element(pairing, G1, value=x1 ** x2)

# this is a test for the BLS short signature system
params = Parameters(param_string=stored_params)
pairing = Pairing(params)

# build the common parameter g
g = Element.random(pairing, G2)

# build the public and private keys
private_key = Element.random(pairing, Zr)
public_key = Element(pairing, G2, value=g ** private_key)

print("private_key = ", private_key)
print("public_key = ", public_key)

# set the magic hash value
hash_value = Element.from_hash(pairing, G1, "hashofmessage")

# create the signature
signature = hash_value ** private_key

# build the temps
temp1 = Element(pairing, GT)
temp2 = Element(pairing, GT)

# fill temp1
temp1 = pairing.apply(signature, g)

# fill temp2
temp2 = pairing.apply(hash_value, public_key)

print(temp1)
print(temp2)
# and again...
temp1 = pairing.apply(signature, g)

if (temp1 == temp2):
    print("true")
else:
    print("false")

# compare to random signature
rnd = Element.random(pairing, G1)
temp1 = pairing.apply(rnd, g)


def compare(self):
    # compare
    self.assertEqual(temp1 == temp2, False)
    print(self.assertEqual(temp1 == temp2, False))