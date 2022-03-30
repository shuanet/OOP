# -*- coding: utf-8 -*-

from ivy.std_api import IvySendMsg
from pyrejeutest.base import IvyPyRejeuTest


class PyRejeuClockTest(IvyPyRejeuTest):
    """
    Test case used to validate that pyrejeu handle
    correcly the clock
    """

    def test_clock_start_stop(self):
        """Test the ClockStart/ClockStop commands"""
        clock_datas = self.get_clock_datas()
        self.assertEqual(clock_datas["Stop"], "1")

        IvySendMsg("ClockStart")
        clock_datas = self.get_clock_datas()
        self.assertEqual(clock_datas["Stop"], "0")

        IvySendMsg("ClockStop")
        clock_datas = self.get_clock_datas()
        self.assertEqual(clock_datas["Stop"], "1")

    def test_set_clock(self):
        """Test the SetClock command"""
        IvySendMsg("SetClock Time=11:54:00")
        current_time = self.get_clock_datas()["Time"]
        self.assertEqual(current_time, "11:54:00")
