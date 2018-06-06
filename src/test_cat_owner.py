from unittest.mock import Mock, MagicMock

from cat_database import CatDatabase
from cat_owner import CatOwner

def test1():
  db = Mock()
  db.getCats = MagicMock(return_value=['샴', '뱅골', '러시안 블루'])

  o = CatOwner(db)

  print('#1: Calling before adoption', o.callCats())

test1()
