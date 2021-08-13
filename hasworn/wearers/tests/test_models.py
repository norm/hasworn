import pytest

from hasworn.wearers.models import Wearer


@pytest.fixture
def wendy(db) -> Wearer:
    return Wearer.objects.create(username='wendy')

def test_get_name(db, wendy) -> None:
    assert Wearer.objects.count() == 1
    assert wendy.username == 'wendy'
    assert wendy.get_short_name() == 'wendy'
    assert wendy.get_full_name() == None
    assert wendy.get_name() == 'wendy'
    wendy.name = 'Wendy Testaburger'
    assert wendy.get_short_name() == 'wendy'
    assert wendy.get_full_name() == 'Wendy Testaburger'
    assert wendy.get_name() == 'Wendy Testaburger'
