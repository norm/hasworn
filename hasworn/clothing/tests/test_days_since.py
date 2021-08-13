from datetime import date
import pytest

from hasworn.clothing.models import Clothing, Wearing, Worn
from hasworn.wearers.models import Wearer


@pytest.fixture
def wendy(db) -> Wearer:
    return Wearer.objects.create(
            username = 'wendy',
            name = 'Wendy Testaburger',
        )

@pytest.fixture
def zone(db, wendy) -> Clothing:
    return Clothing.objects.create(
            name = 'In the Zone',
            created_by = wendy,
        )

@pytest.fixture
def worn(db, wendy, zone) -> Worn:
    return Worn.objects.create(wearer=wendy, clothing=zone)

@pytest.fixture
def wearings(db, worn):
    Wearing.objects.create(worn=worn, day=date(2018, 1, 1))
    Wearing.objects.create(worn=worn, day=date(2018, 2, 1))
    Wearing.objects.create(worn=worn, day=date(2018, 2, 10))

def test_days_since_is_saved(db, wendy, wearings):
    shirt = wendy.worn_set.all()[0]
    assert shirt.days_worn.count() == 3
    first = shirt.days_worn.all().order_by('day')[0]
    assert first.days_since_last == None
    latest = shirt.days_worn.all().order_by('-day')[0]
    assert latest.days_since_last == 9

def test_insert_older_wearing_adjusts_days_since(db, wendy, worn, wearings):
    shirt = wendy.worn_set.all()[0]
    assert shirt.days_worn.count() == 3
    latest = shirt.days_worn.all().order_by('-day')[0]
    assert latest.days_since_last == 9
    new = Wearing.objects.create(worn=worn, day=date(2018, 2, 8))
    latest = shirt.days_worn.all().order_by('-day')[0]
    assert latest.days_since_last == 2
