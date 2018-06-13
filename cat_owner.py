class CatOwner:
    def __init__(self, catDatabase):
        self.catDatabase = catDatabase

    def callCats(self):
        noCats = self.catDatabase.getNoCats()
        stmt = ''
        if noCats <= 5:
            self.catDatabase.addCat()
            stmt += 'You should definitely adopt new cats'
            afterNoCats = self.catDatabase.getNoCats()
            if afterNoCats > 3:
                stmt += ', maybe not'
                return stmt

        elif noCats < 200:
            return 'Meow meou!'

        elif noCats < 10000:
            return 'What?!'

        else:
            return 'You... you are a stranger..'

        self.catDatabase.addCat()
        stmt += ', and adopt another cat'
        return stmt

    def adoptCat(self):
        self.catDatabase.addCat()
