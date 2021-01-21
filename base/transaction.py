import binascii
import struct
from collections import OrderedDict

from Crypto.PublicKey import RSA

from base.utils import compat_bytes, bigint_to_bytes
from base.utxo import UTXO


class Transaction:
    class Input:
        def __init__(self, prevHash: bytes, index: int, signature: bytes = None):
            if prevHash is None:
                self._prevTxHash = None
            else:
                self._prevTxHash = prevHash

            self._outputIndex = index

            if signature is None:
                self._signature = None
            else:
                self._signature = signature

        @property
        def prevTxHash(self):
            return self._prevTxHash

        @property
        def outputIndex(self):
            return self._outputIndex

        @property
        def signature(self):
            return self._signature

        def __eq__(self, other):
            if other is None:
                return False

            if isinstance(other, Transaction.Input):
                return (self.prevTxHash == other.prevTxHash
                        and self.outputIndex == other.outputIndex
                        and self.signature == other.signature)

            return False

        def __hash__(self):
            if self.signature is None:
                sig = hash(None)
            else:
                sig = hash(frozenset(self.signature))
            return hash(frozenset(self.prevTxHash)) ^ hash(self.outputIndex) ^ sig

        def addSignature(self, sig: bytes):
            if sig is None:
                self._signature = None
            else:
                self._signature = sig

        def to_dict(self):
            return OrderedDict({'prevTxHash': binascii.hexlify(self.prevTxHash).decode('ascii'),
                                'outputIndex': self.outputIndex,
                                'signature': binascii.hexlify(self.signature).decode('ascii')})

    class Output:
        def __init__(self, v: float, pk):
            self._value = v
            if isinstance(pk, RSA.RsaKey):
                self._address = pk
            else:
                self._address = RSA.importKey(binascii.unhexlify(pk))

        @property
        def value(self):
            return self._value

        @property
        def address(self):
            return self._address

        def __eq__(self, other):
            if other is None:
                return False

            if isinstance(other, Transaction.Output):
                return (self.value == other.value
                        and self.address == other.address)

            return False

        def __hash__(self):
            # return hash(self.value) ^ hash(self.address)
            _hash = 1
            _hash = _hash * 17 + int(self.value) * 10000
            _hash = _hash * 31 + hash(self.address.e)
            _hash = _hash * 31 + hash(self.address.n)
            return _hash

        def to_dict(self):
            return OrderedDict({'value': self.value,
                                'address': binascii.hexlify(self.address.exportKey(format='DER')).decode('ascii')})

    def __init__(self, tx=None):

        if tx is None:
            self._inputs = []
            self._outputs = []
            self._hash = None
        else:
            self._inputs = tx.inputs
            self._outputs = tx.outputs
            self._hash = tx.hash
        self._coinbase = False

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def hash(self):
        return self._hash

    @property
    def coinbase(self):
        return self._coinbase

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, Transaction):
            if self.numInputs() != other.numInputs():
                return False
            for i in range(self.numInputs()):
                if not self.getInput(i) == other.getInput(i):
                    return False
            if self.numOutputs() != other.numOutputs():
                return False
            for i in range(self.numOutputs()):
                if not self.getOutput(i) == other.getOutput(i):
                    return False
            return True

        return False

    def __hash__(self):
        _hash = 1
        for i in range(self.numInputs()):
            _hash = _hash * 31 + hash(self._inputs[i])
        for i in range(self.numOutputs()):
            _hash = _hash * 31 + hash(self._outputs[i])
        return _hash

    def addInput(self, prevTxHash, outputIndex):
        inp = Transaction.Input(prevTxHash, outputIndex)
        self._inputs.append(inp)

    def addOutput(self, value, address):
        op = Transaction.Output(value, address)
        self._outputs.append(op)

    def addSignature(self, signature, index):
        self._inputs[index].addSignature(signature)

    def removeInput(self, index: int):
        if index >= len(self._inputs):
            raise AttributeError("Index out of range")
        self._inputs = self._inputs[:index] + self._inputs[index + 1:]

    def removeInputWithUTXO(self, ut: UTXO):
        for index, inp in self._inputs:
            u = UTXO(inp.prevTxHash, inp.outputIndex)
            if u == ut:
                self._inputs = self._inputs[:index] + self._inputs[index + 1:]
                return

    def getRawDataToSign(self, index: int) -> bytes:
        # produces data repr for  ith=index input and all outputs
        sigData = b""
        if index > len(self._inputs):
            return sigData

        inp = self.inputs[index]
        sigData += inp.prevTxHash
        # performs conversions between Python values and C structs represented as Python bytes objects.
        # native integer 4-bytes
        sigData += struct.pack("<i", inp.outputIndex)

        for op in self.outputs:
            sigData += struct.pack("<d", op.value)
            # using pycryptodome lib
            # e: RSA public exponent
            sigData += compat_bytes(op.address.e)
            # n: RSA modulus
            sigData += bigint_to_bytes(op.address.n)

        return sigData

    def getRawTx(self) -> bytes:
        rawTx = b""
        for inp in self.inputs:
            rawTx += inp.prevTxHash
            rawTx += struct.pack("<i", inp.outputIndex)
            rawTx += inp.signature

        for op in self.outputs:
            # native double 8-bytes
            rawTx += struct.pack("<d", op.value)
            rawTx += compat_bytes(op.address.e)
            rawTx += bigint_to_bytes(op.address.n)

        return rawTx

    def finalize(self):
        import hashlib
        md = hashlib.sha256()
        md.update(self.getRawTx())
        self._hash = md.hexdigest()

    def getInput(self, index: int) -> Input:
        if index < len(self.inputs):
            return self.inputs[index]
        raise AttributeError("Index out of range")

    def getOutput(self, index: int) -> Output:
        if index < len(self.outputs):
            return self.outputs[index]
        raise AttributeError("Index out of range")

    def numInputs(self):
        return len(self.inputs)

    def numOutputs(self):
        return len(self.outputs)

    def isCoinbase(self):
        return self.coinbase
