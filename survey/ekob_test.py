import pytest
import datetime
import pytest_django


from django.urls import reverse, resolve

from survey.functions import validity_date


@pytest.mark.parametrize("date, period, expected", (
        (datetime.datetime(2011, 8, 31), 6, datetime.datetime(2012, 2, 29)),
        (datetime.datetime(2012, 8, 31), 6, datetime.datetime(2013, 2, 28)),
        (datetime.datetime(2015, 8, 31), 1, datetime.datetime(2015, 9, 30)),
        (datetime.datetime(2016, 11, 1), 6, datetime.datetime(2017, 4, 30)),
        (datetime.datetime(2018, 1, 1), 1, datetime.datetime(2018, 1, 31)),

))
def test_date(date, period, expected):
    assert validity_date(date, period) == expected

def test_url_update_survey():
    path = reverse('update_survey', kwargs={'survey_id':4})
    assert resolve(path).view_name=='update_survey'

# @pytest.mark.django_db