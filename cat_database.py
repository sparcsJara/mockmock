class CatDatabase:
    def __init__(self):
        self.noCats = 0

    def getNoCats(self) -> int:
        return self.noCats

    def addCat(self, newCat) -> int:
        self.noCats += 1
        return self.noCats
