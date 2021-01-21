class UTXO:
    def __init__(self, txHash: bytes, index: int):
        self._txHash = txHash
        self._index = index

    def getTxHash(self):
        return self._txHash

    def getIndex(self):
        return self._index

    def __hash__(self):
        return hash((self._index, self._txHash))

    def __eq__(self, other):
        return self._compare(other) == 0

    def __gt__(self, other):
        return self._compare(other) == 1

    def __lt__(self, other):
        return self._compare(other) == -1

    def _compare(self, other):
        if self._index > other._index:
            return 1
        if self._index < other._index:
            return -1
        if self._txHash > other._txHash:
            return 1
        if self._txHash < other._txHash:
            return -1
        return 0


class UTXOPool:
    def __init__(self):
        self._map = dict()

    def addUTXO(self, utxo: UTXO, txOut):
        self._map[utxo] = txOut

    def removeUTXO(self, utxo: UTXO):
        self._map.pop(utxo)

    def getTxOutput(self, utxo: UTXO):
        return self._map.get(utxo)

    def contains(self, utxo: UTXO):
        return utxo in self._map

    def getAllUTXO(self):
        return list(self._map.keys())


# tests
if __name__ == "__main__":
    u1 = UTXO(b'aaaa', 1)
    u2 = UTXO(b'bbbb', 2)
    u3 = UTXO(b'aaaa', 1)
    u4 = UTXO(b'aaab', 1)
    assert u1 < u2
    assert u1 == u3
    assert hash(u1) != hash(u2)
    assert hash(u1) == hash(u3)
    assert u4 > u3
    assert u3 < u4

    p = UTXOPool()
    p.addUTXO(u1, 1)
    assert p.getTxOutput(u1) == 1
    assert p.getAllUTXO() == [u1]
    p.removeUTXO(u1)
    assert p.contains(u1) == False
