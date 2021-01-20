import struct

from base.utils import compat_bytes
from base.utxo import UTXO


class Transaction:
    class Input:
        def __init__(self, prevHash, index, signature=None):
            if prevHash is None:
                self.prevTxHash = None
            else:
                self.prevTxHash = prevHash

            self.outputIndex = index

            if signature is None:
                self.signature = None
            else:
                self.signature = signature

        def __eq__(self, other):
            if other is None:
                return False

            if isinstance(other, Transaction.Input):
                return (self.prevTxHash == other.prevTxHash
                        and self.outputIndex == other.outputIndex
                        and self.signature == other.signature)

            return False

        def __hash__(self):
            #
            # return id(self.prevTxHash) ^ hash(self.index) ^ id(self.signature)
            #
            if self.signature is None:
                sig = hash(None)
            else:
                sig = hash(frozenset(self.signature))
            return hash(frozenset(self.prevTxHash)) ^ hash(self.outputIndex) ^ sig

        def addSignature(self, sig):
            if sig is None:
                self.signature = None
            else:
                self.signature = sig

    class Output:
        def __init__(self, v, pk):
            self.value = v
            self.address = pk

        def __eq__(self, other):
            if other is None:
                return False

            if isinstance(other, Transaction.Output):
                return (self.value == other.value
                        and self.address == other.address)
            return False

        def __hash__(self):
            return hash(self.value) ^ hash(self.address)

    def __init__(self, tx=None):
        self.inputs = []
        self.outputs = []
        self.coinbase = False
        if tx is not None:
            self.hash = tx.hash
        else:
            self.hash = None

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
        hash_ = 1
        for i in range(self.numInputs()):
            hash_ = hash_ * 31 + hash(self.inputs[i])
        for i in range(self.numOutputs()):
            hash_ = hash_ * 31 + hash(self.outputs[i])
        return hash_

    def addInput(self, prevTxHash, outputIndex):
        inp = Transaction.Input(prevTxHash, outputIndex)
        self.inputs.append(inp)

    def addOutput(self, value, address):
        op = Transaction.Output(value, address)
        self.outputs.append(op)

    def removeInput(self, index: int):
        self.inputs.remove(index)

    def removeInput(self, ut: UTXO):
        # Wait UTXO class
        for index, inp in self.inputs:
            u = UTXO(inp.prevTxHash, inp.outputIndex)
            if u == ut:
                self.inputs.remove(index)
                return

    def getRawDataToSign(self, index):
        # produces data repr for  ith=index input and all outputs
        sigData = b""
        if index > len(self.inputs):
            return None

        inp = self.inputs[index]
        sigData += struct.pack("<i", inp.outputIndex)
        sigData += inp.prevTxHash

        for op in self.outputs:
            sigData += struct.pack("<d", op.value)
            # TODO: need convert object PublicKey to bytes value
            # using pycryptodome lib
            sigData += compat_bytes(op.address)

        return sigData

    def addSignature(self, signature, index):
        self.inputs[index].addSignature(signature)

    def getRawTx(self):
        rawTx = b""
        for inp in self.inputs:
            rawTx += inp.prevTxHash
            # performs conversions between Python values and C structs represented as Python bytes objects.
            # native integer 4-bytes
            rawTx += struct.pack("<i", inp.outputIndex)
            rawTx += inp.signature

        for op in self.outputs:
            # native double 8-bytes
            rawTx += struct.pack("<d", op.value)
            # TODO: need convert object PublicKey to bytes value
            rawTx += compat_bytes(op.address)

        return rawTx

    def finalize(self):
        import hashlib
        md = hashlib.sha256()
        md.update(self.getRawTx())
        self.hash = md.hexdigest()

    def getInput(self, index):
        if index < len(self.inputs):
            return self.inputs[index]
        return None

    def getOutput(self, index):
        if index < len(self.outputs):
            return self.outputs[index]
        return None

    def numInputs(self):
        return len(self.inputs)

    def numOutputs(self):
        return len(self.outputs)

    def isCoinbase(self):
        return self.coinbase
