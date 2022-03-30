# -*- coding: utf-8 -*-

import unittest
from pyrejeu.utils import str_to_sec
from pyrejeu.utils import sec_to_str
from pyrejeu.utils import modulo_min_max
from pyrejeu.utils import turn_orientation
from pyrejeu.utils import get_heading
from pyrejeu.utils import turn
from pyrejeu.utils import dist


class UtilsTest(unittest.TestCase):
    """Test case use to validate functions of the module 'utils'."""

    def setUp(self):
        """Test init"""
        self.hour_str = "12:54:27"
        self.hour_sec = 12*3600+54*60+27

    def test_str_to_sec(self):
        """test the function that convert 'HH:MM:SS' into seconds"""
        value = str_to_sec(self.hour_str)
        self.assertEqual(value, self.hour_sec)

    def test_sec_to_str(self):
        """Test the function the converts seconds into 'HH:MM:SS'"""
        string = sec_to_str(self.hour_sec)
        self.assertEqual(string, self.hour_str)

    def test_modulo_min_max(self):
        """Test modulo min/max function"""
        self.assertEqual(90.0, modulo_min_max(90.0, 0, 360))
        self.assertEqual(90.0, modulo_min_max(-270.0, 0, 360))
        self.assertEqual(10.0, modulo_min_max(370.0, 0, 360))

    def test_turn_orientation(self):
        """Test turn orientation function"""
        self.assertEqual("Left", turn_orientation(10.0, 350.0))
        self.assertEqual("Right", turn_orientation(350.0, 10.0))

    def test_get_heading(self):
        """Test get_heading function"""
        self.assertEqual(45.0, get_heading(1.0, 1.0))
        self.assertEqual(0.0, get_heading(0.0, 1.0))
        self.assertEqual(90.0, get_heading(1.0, 0.0))

    def test_turn(self):
        """Test the turn function"""
        rate, inc_time = -3.0, 8.0
        c_heading, t_heading = 10.0, 350.0
        self.assertEqual(350.0, turn(c_heading, t_heading, rate, inc_time))
        c_heading, t_heading = 350.0, 300.0
        self.assertEqual(326.0, turn(c_heading, t_heading, rate, inc_time))

        rate, inc_time = 3.0, 4.0
        c_heading, t_heading = 170.0, 180.0
        self.assertEqual(180.0, turn(c_heading, t_heading, rate, inc_time))
        c_heading, t_heading = 170.0, 250.0
        self.assertEqual(182.0, turn(c_heading, t_heading, rate, inc_time))

    def test_dist(self):
        """Test the dist function"""
        A = {"pos_x": 15, "pos_y": 30}
        B = {"pos_x": 150, "pos_y": 120}
        self.assertEqual(int(dist(A, B)), 162)
