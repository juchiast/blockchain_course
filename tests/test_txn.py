import binascii
import unittest

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5

from base.transaction import Transaction

genesisPublicKey = RSA.import_key(open('genesis_public.pem', 'r').read())
genesisPrivateKey = RSA.import_key(open('genesis_private.pem', 'r').read())
alicePublicKey = RSA.import_key(open('alice_public.pem', 'r').read())
alicePrivateKey = RSA.import_key(open('alice_private.pem', 'r').read())
bobPublicKey = RSA.import_key(open('bob_public.pem', 'r').read())
bobPrivateKey = RSA.import_key(open('bob_private.pem', 'r').read())


def sign(privateKey, tx, index):
    # Takes msg and sk and outputs signature for msg
    hashMsg = SHA256.new(tx.getRawDataToSign(index))
    signer = PKCS1_v1_5.new(privateKey)
    signature = signer.sign(hashMsg)
    return signature


def verify(publicKey, signature, msg):
    # Takes msg public key and signature and returns boolean
    hashMsg = SHA256.new(msg)
    verifier = PKCS1_v1_5.new(publicKey)
    try:
        verifier.verify(hashMsg, binascii.unhexlify(signature))
        return True
    except:
        return False


class MyTestCase(unittest.TestCase):

    def testOutput(self):
        op1 = Transaction.Output(5, alicePublicKey)
        op2 = Transaction.Output(5, bobPublicKey)
        op3 = Transaction.Output(5, alicePublicKey)

        assert op1 != op2

        assert hash(op1) == hash(op3)

        assert hash(op2) != hash(op3)

    def testInput(self):
        inp1 = Transaction.Input(b'abcdef', 0)
        inp2 = Transaction.Input(b'abcdef', 1)
        inp3 = Transaction.Input(b'abcdefg', 0)
        inp4 = Transaction.Input(b'abcdef', 1)

        assert inp1 != inp2

        assert hash(inp1) != hash(inp2)

        assert hash(inp2) != hash(inp3)

        assert hash(inp2) == hash(inp4)

    def testTransaction(self):
        tx = Transaction()

        tx.addInput(b'genesis', 0)
        assert tx.numInputs() == 1

        opGenesis = Transaction.Output(5, genesisPublicKey)
        tx.addOutput(opGenesis.value, opGenesis.address)
        tx.addOutput(5, alicePublicKey)
        tx.addOutput(10, bobPublicKey)
        assert tx.numOutputs() == 3

        tx.removeInput(0)
        assert tx.numInputs() == 0

        tx.addInput(b'genesis', 0)
        signature0 = sign(genesisPrivateKey, tx, 0)
        tx.addSignature(signature0, 0)
        tx.finalize()

        print(tx.hash)
        print(hash(tx.getInput(0)))
        print(tx.getInput(0).to_dict())
        print(hash(tx.getOutput(0)))
        print(tx.getOutput(0).to_dict())

        print(verify(genesisPublicKey, binascii.hexlify(signature0).decode('ascii'), tx.getRawDataToSign(0)))


if __name__ == '__main__':
    unittest.main()
