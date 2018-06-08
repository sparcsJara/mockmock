from cat_database import CatDatabase
from cat_owner import CatOwner

def test1():
    db = CatDatabase()
    o = CatOwner(db)

    assert o.callCats() == 'Lonely cat meowed..'

    for i in range(4):
        o.adoptCat()

    # 실제로 위의 for 문이 무지 복잡해서 고양이 분양받기가 네 번 일어났는지 검증하고 싶었다고 칩시다..
    assert db.addCat.call_count == 4


if __name__ == '__main__':
    test1()
