# -*- coding: utf-8 -*-

import unittest
import os
from pyrejeutest.utils.databuilder import TestData
from pyrejeu.db.models import Beacon, Flight
from pyrejeu.db.connection import DatabaseConnection
from pyrejeu.db.importations import RejeuImportation
from pyrejeu.utils import str_to_sec


class ImportationTest(unittest.TestCase):
    """Test case used to validate the importation of rejeu files"""

    @classmethod
    def setUpClass(cls):
        cls.test_data = TestData()
        db_name = "{0}.db".format(cls.test_data.get_random_string())
        cls.db_file = os.path.join("/tmp", db_name)
        if os.path.isfile(cls.db_file):
            os.unlink(cls.db_file)
        cls.db_connection = DatabaseConnection(file_path=cls.db_file)
        import_obj = RejeuImportation(None, cls.db_connection)
        import_obj.import_file(cls.test_data.get_trafic_data_file(),
                               event=False)

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.db_file):
            os.unlink(cls.db_file)

    def setUp(self):
        """Test setup"""
        self.session = self.db_connection.get_session()

    def tearDown(self):
        """Test tear down"""
        self.session.close()

    def test_beacons(self):
        """Test the importation of beacons"""
        beacons = self.session.query(Beacon).all()
        self.assertEqual(len(beacons), 1850)

        self.assertEqual(beacons[2].name, "ENOBU")

    def test_flights(self):
        """Test the importation of flights"""
        flights = self.session.query(Flight).all()
        self.assertEqual(len(flights), 2)

        flight_ids = [flight.id for flight in flights]
        self.assertListEqual(flight_ids, [10001, 10002])

    def test_cones(self):
        """Test the importation of cones"""
        flight = self.session.query(Flight).get(10002)
        cones = flight.cones
        self.assertEqual(len(cones), 355)

        first_cone = cones[0]
        self.assertEqual(first_cone.hour, str_to_sec("11:24:00"))

