from checks.parked import Parked
from mock import patch, MagicMock
from nose.tools import assert_true


class TestParked():

    def __init__(self):
        self._park = Parked()
        self.domain = 'comicsn.tech'

    def test_is_parked(self):
        pass
