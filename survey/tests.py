
import unittest

from survey.functions import validity_date
import datetime



class DateTest(unittest.TestCase):
    def test_date1(self):
        date_s=datetime.date(2011, 8, 31)
        result = validity_date(date_s, 6)
        expected = datetime.datetime(2012, 2, 29)
        self.assertEqual(expected, result)

    def test_date2(self):
        date_s=datetime.date(2012, 8, 31)
        result = validity_date(date_s, 6)
        expected = datetime.datetime(2013, 2, 28)
        self.assertEqual(expected, result)

    def test_date3(self):
        date_s=datetime.date(2015, 8, 31)
        result = validity_date(date_s, 1)
        expected = datetime.datetime(2015, 9, 30)
        self.assertEqual(expected, result)

    def test_date4(self):
        date_s=datetime.date(2016, 11, 1)
        result = validity_date(date_s, 6)
        expected = datetime.datetime(2017, 4, 30)
        self.assertEqual(expected, result)

    def test_date5(self):
        date_s=datetime.date(2018, 1, 1)
        result = validity_date(date_s, 1)
        expected = datetime.datetime(2018, 1, 31)
        self.assertEqual(expected, result)




if __name__ == "__main__":
    unittest.main()
