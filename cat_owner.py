class CatOwner:
  def __init__(self, catDatabase):
    self.catDatabase = catDatabase

  def callCats(self):
    noCats = self.catDatabase.getNoCats()
    if noCats == 0:
      return 'No cat'
    elif noCats == 1:
      return 'Lonely cat meowed..'
    elif noCats == 2:
      return 'Meow meou!'
    else:
      return 'Meooooow~'

  def adoptCat(self):
    self.catDatabase.addCat()
