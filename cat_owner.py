class CatOwner:
    def __init__(self, catDatabase):
        self.catDatabase = catDatabase

    def callCats(self):
        noCats = self.catDatabase.getNoCats()
        if noCats <= 0:
            return 'No cat'

        elif noCats == 1:
            return 'Lonely cat meowed..'

        else:
            if noCats < 200:
                return 'Meow meou!'

            else if noCats < 10000:
                return 'What?!'

            else:
                return 'You... you are strange..'

    def adoptCat(self):
        self.catDatabase.addCat()
