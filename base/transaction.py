class Transaction:
    class Input:
        def __init__(self, prevHash, index):
            if prevHash is None:
                self.prevTxHash = None
            else:
                self.prevTxHash = prevHash
            self.outputIndex = index

        def __eq__(self, other):
            # Write your code here
            # return a boolean
            return False

        def __hash__(self):
            # Write your code here
            # return an int
            return 0

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
            # Write your code here
            # return a boolean
            return False

        def __hash__(self):
            # Write your code here
            # return an int
            return 0

    def __init__(self, tx=None):
        self.inputs = []
        self.outputs = []
        self.coinbase = False
        if tx is not None:
            self.hash = tx.hash
        else:
            self.hash = None

    def __eq__(self, other):
        # Write your code here
        # return a boolean
        return False

    def __hash__(self):
        # Write your code here
        # return an int
        return 0

    def addInput(self, prevTxHash, outputIndex):
        inp = Transaction.Input(prevTxHash, outputIndex)
        self.inputs.append(inp)

    def addOutput(self, value, address):
        op = Transaction.Output(value, address)
        self.outputs.append(op)

    def removeInput(self, index):
        self.inputs.remove(index)

    def removeInput(self, ut):
        # Wait UTXO class
        # for in in self.inputs:
        #     u = UTXU(in.prevTxHash, in.outputIndex)
        #     if u.equals(ut):
        #         self.inputs.remove(u)
        return

    def getRawDataToSign(self, index):
        # produces data repr for  ith=index input and all outputs
        # Write your code here
        # return byte array
        sigData = ""
        return sigData

    def addSignature(self, signature, index):
        self.inputs[index].addSignature(signature)

    def getRawTx(self):
        rawTx = ""
        for inp in self.inputs:
            rawTx += inp.prevTxHash
            rawTx += inp.outputIndex
            rawTx += inp.signature

        for op in self.outputs:
            rawTx += str(op.value)
            rawTx += op.address

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
