from unittest.mock import patch
from cat_database import CatDatabase
from instrumented_cat_owner import CatOwner


@patch('cat_database.CatDatabase')
def test1(arg0, arg1, db):
    db.getNoCats.return_value = arg0
    db.addCat.return_value = arg1
    o = CatOwner(db)
    assert o.callCats() == 'Lonely cat meowed..'
    for i in range(4):
        o.adoptCat()
    assert db.addCat.call_count == 4


if __name__ == '__main__':
    test1()
