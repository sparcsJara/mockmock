class CatDatabase:
    ''' 실제론 데이터베이스에 직접 접속해서 느리다고 합시다 '''
    def __init__(self):
        self.noCats = 0

    def getNoCats(self) -> int:
        return self.noCats

    def addCat(self) -> int:
        self.noCats += 1
        return self.noCats
