class CatOwner:
  def __init__(self, catDatabase):
    self.catDatabase = catDatabase

  def callCats(self):
    cats = self.catDatabase.getCats()
    if (len(cats) == 0):
      return 'No cat'
    else:
      return ", ".join(cats)
        

  def adoptCat(self, newCat):
    self.catDatabase.addCat(newCat)
