class CatOwner:

    def __init__(self, catDatabase):
        self.catDatabase = catDatabase

    def callCats(self):
        noCats = self.catDatabase.getNoCats()
        TDG_l, TDG_r = noCats, 0
        print('TDG', 'V', '1', TDG_l, TDG_r, type(TDG_l).__name__, type(
            TDG_r).__name__)
        if TDG_l == TDG_r:
            print('TDG', 'B', '1', 'T')
            return 'No cat'
        else:
            print('TDG', 'B', '1', 'F')
            TDG_l, TDG_r = noCats, 1
            print('TDG', 'V', '2', TDG_l, TDG_r, type(TDG_l).__name__, type
                (TDG_r).__name__)
            if TDG_l == TDG_r:
                print('TDG', 'B', '2', 'T')
                return 'Lonely cat meowed..'
            else:
                print('TDG', 'B', '2', 'F')
                TDG_l, TDG_r = noCats, 2
                print('TDG', 'V', '3', TDG_l, TDG_r, type(TDG_l).__name__,
                    type(TDG_r).__name__)
                if TDG_l == TDG_r:
                    print('TDG', 'B', '3', 'T')
                    return 'Meow meou!'
                else:
                    print('TDG', 'B', '3', 'F')
                    return 'Meooooow~'

    def adoptCat(self):
        self.catDatabase.addCat()
