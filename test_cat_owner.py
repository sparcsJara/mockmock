from cat_database import CatDatabase
from cat_owner import CatOwner

def test1(db):

  o = CatOwner(db)

  print('#1: Calling before adoption\n> ', o.callCats())

  for i in range(4):
    o.adoptCat()

  print('#2: Calling after adopting many cats\n> ', o.callCats())

  # 실제로 위의 for 문이 무지 복잡해서 고양이 분양받기가 네 번 일어났는지 검증하고 싶었다고 칩시다..
  assert db.addCat.call_count == 4

test1()
