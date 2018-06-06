class CatDatabase:
  def __init__(self):
    self.cats = ['샴', '뱅골', '러시안 블루']

  def getCats(self):
    return self.cats

  def addCat(self, newCat):
    self.cats.append(newCat)
