class CatDatabase:
  def __init__(self):
    self.noCats = 0

  def getNoCats(self):
    return self.noCats

  def addCat(self, newCat):
    self.noCats += 1
