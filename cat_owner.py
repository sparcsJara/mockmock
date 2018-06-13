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

        elif noCats < 9999:
            return 'What?!'

        else:
            self.catDatabase.addCat()
            if self.catDatabase.getNoCats() == 10000:
                return 'Perfect 10000!'
            
            return 'You... you are a stranger..'

        self.catDatabase.addCat()
        stmt += ', and adopt another cat'
        return stmt

    def adoptCat(self):
        self.catDatabase.addCat()
