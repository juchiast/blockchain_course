class UTXO:
    def __init__(self, txHash, index):
        self.txHash = txHash
        self.index = index

    def getTxHash(self):
        return self.txHash

    def getIndex(self):
        return self.index

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, UTXO):
            return (self.txHash == other.txHash
                    and self.index == other.index)
        return False

    def __hash__(self):
        hash_ = 1
        hash_ = hash_ * 17 + self.index
        hash_ = hash_ * 31 + hash_(self.txHash)
        return hash_
