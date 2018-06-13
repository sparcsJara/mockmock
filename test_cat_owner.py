from cat_database import CatDatabase
from cat_owner import CatOwner

def test1():
    db = CatDatabase()
    o = CatOwner(db)

    # assert o.callCats() == 'You should definitely adopt new cats, and adopt another cat'
    o.callCats()
    o.adoptCat()

    # 실제로 위 과정이 무지 복잡해서 고양이 분양받기가 실제로 일어났는지 검증하고 싶었다고 칩시다
    assert db.addCat.call_count >= 1


if __name__ == '__main__':
    test1()
