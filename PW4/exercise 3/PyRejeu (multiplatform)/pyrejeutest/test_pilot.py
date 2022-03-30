# -*- coding: utf-8 -*-

import re
import time
from threading import Event
from ivy.std_api import IvySendMsg
from ivy.std_api import IvyBindMsg
from ivy.std_api import IvyUnBindMsg
from pyrejeutest.base import IvyPyRejeuTest
from pyrejeu.utils import str_to_sec, get_heading, min_dist_to_beacon


class AircraftPilotTest(IvyPyRejeuTest):
    """
    Test case used to validate that pyrejeu answer
    correcly to aircraft pilot commands
    """

    def __parse_traj(self, trajectory):
        trajectory = re.findall(r"\S+ \S+ \S+ \S+", trajectory)
        trajectory = [t.split() for t in trajectory]
        return [{
            "hour": str_to_sec(hour),
            "pos_x": float(x),
            "pos_y": float(y),
            "fl": int(fl)
        } for x, y, hour, fl in trajectory]

    def __test_wrong_command(self, orders):
        self.__report_result = None
        self.__report_evt = Event()

        def on_report_msg(agent, *larg):
            self.__report_evt.set()
            self.__report_result = larg[1]

        s_id = IvyBindMsg(on_report_msg, "ReportEvent (.*) Result=(.*) "
                          "Info=(.*) Order=(.*)")
        for order in orders:
            IvySendMsg(order)
            time.sleep(0.1)

        self.assertTrue(self.__report_evt.wait(timeout=3.0),
                        "Report Event is not received")
        IvyUnBindMsg(s_id)
        self.assertEqual(self.__report_result, "ERROR")

    def test_wrong_flight(self):
        """Valid the behavior of pyrejeu when we give a wrong flight number"""
        f_id = 51
        t_heading = 180

        orders = [
            "SetClock Time=12:09:00",
            "AircraftHeading Flight={0} To={1}".format(f_id, t_heading)
        ]
        self.__test_wrong_command(orders)

    def test_turn(self):
        """Test the AircraftTurn command"""
        f_id = 10001
        t_angle = 30

        IvySendMsg("SetClock Time=12:05:00")
        time.sleep(0.1)
        IvySendMsg("AircraftTurn Flight={0} Angle={1}".format(f_id, t_angle))
        time.sleep(0.1)
        trajectory = self.get_track(f_id)

        # verify that the new trajectory follows the right heading
        order_time = str_to_sec("12:05:00")
        verif_time = str_to_sec("12:10:00")
        p_cone, t_heading = None, None
        for cone in trajectory:
            hour = str_to_sec(cone["hour"])
            if hour > order_time and t_heading is None:
                t_heading = int(get_heading(p_cone["vit_x"], p_cone["vit_y"])
                                + t_angle)
            if hour > verif_time:
                v_y = cone["vit_y"]
                v_x = cone["vit_x"]
                self.assertEqual(t_heading, int(get_heading(v_x, v_y)))
            p_cone = cone

        # reset change
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))

    def test_heading(self):
        """Test the AircraftHeading command"""
        f_id = 10001
        t_heading = 180

        IvySendMsg("SetClock Time=12:09:00")
        time.sleep(0.1)
        IvySendMsg("AircraftHeading Flight={0} To={1}".format(f_id, t_heading))
        time.sleep(0.1)
        trajectory = self.__parse_traj(self.get_trajectory(f_id))

        # verify that the new trajectory follows the right heading
        order_time = str_to_sec("12:12:00")
        p_cone = None
        for cone in trajectory:
            if cone["hour"] > order_time and p_cone is not None:
                v_x = cone["pos_x"] - p_cone["pos_x"]
                v_y = cone["pos_y"] - p_cone["pos_y"]
                self.assertEqual(t_heading, get_heading(v_x, v_y))
            p_cone = cone

        # reset change
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))

    def test_heading_maintain(self):
        """Test the AircraftHeading command with maintain option"""
        f_id = 10001
        m_heading = int(get_heading(-101.0, 64))

        IvySendMsg("SetClock Time=12:10:50")
        time.sleep(0.1)
        IvySendMsg("AircraftHeading Flight={0} To=Maintain".format(f_id))
        time.sleep(0.1)
        trajectory = self.__parse_traj(self.get_trajectory(f_id))

        # verify that the new trajectory follows the right heading
        order_time = str_to_sec("12:10:50")
        p_cone = None
        for cone in trajectory:
            if cone["hour"] > order_time and p_cone is not None:
                v_x = cone["pos_x"] - p_cone["pos_x"]
                v_y = cone["pos_y"] - p_cone["pos_y"]
                r = range(m_heading-3, m_heading+3)
                self.assertTrue(int(get_heading(v_x, v_y)) in r)
            p_cone = cone

        # reset change
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))

    def test_heading_wrong_heading(self):
        """Test the AircraftHeading command with wrong heading"""
        f_id = 10001
        heading = self.test_data.get_random_string()
        orders = [
            "SetClock Time=12:00:00",
            "AircraftHeading Flight={0} To={1}".format(f_id, heading)
        ]
        self.__test_wrong_command(orders)

    def test_direct(self):
        """Test the AircraftDirect command"""
        f_id = 10001
        beacon_name = "BTZ"
        beacon, pln_beacon = self.get_beacons([beacon_name, "AGN"])

        IvySendMsg("SetClock Time=11:59:00")
        time.sleep(0.1)
        IvySendMsg("AircraftDirect Flight={0} "
                   "Beacon={1}".format(f_id, beacon_name))
        time.sleep(0.1)
        trajectory = self.__parse_traj(self.get_trajectory(f_id))
        dist, cone = min_dist_to_beacon(trajectory, beacon)
        self.assertTrue(dist < 1.0)

        dist, cone = min_dist_to_beacon(trajectory, pln_beacon)
        self.assertTrue(dist > 10)

        # now resume flight plan
        IvySendMsg("SetClock Time=12:05:00")
        time.sleep(1)
        IvySendMsg("AircraftDirect Flight={0} Beacon=RESUME_PLN".format(f_id))
        time.sleep(1)
        trajectory = self.__parse_traj(self.get_trajectory(f_id))
        dist, cone = min_dist_to_beacon(trajectory, pln_beacon)
        self.assertTrue(dist < 1)

        # reset change
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))

    def test_direct_wrong_beacon(self):
        """Test the AircraftDirect command with wrong beacon"""
        f_id = 10001
        beacon_name = self.test_data.get_random_string()
        orders = [
            "SetClock Time=12:00:00",
            "AircraftDirect Flight={0} Beacon={1}".format(f_id, beacon_name)
        ]
        self.__test_wrong_command(orders)

    def test_range_event(self):
        """Test the emission of the RangeUpdateEvent message"""
        f_id = 10001
        evt = Event()
        range_infos = {}

        def on_range_event(agent, *larg):
            evt.set()
            range_infos.update({
                "first": larg[0],
                "last": larg[1]
            })

        s_id = IvyBindMsg(on_range_event, "RangeUpdateEvent FirstTime=(\S+) "
                          "LastTime=(\S+)")
        # extend the trajectory
        IvySendMsg("SetClock Time=12:30:00")
        time.sleep(0.1)
        IvySendMsg("AircraftHeading Flight={0} To={1}".format(f_id, 0))
        self.assertTrue(evt.wait(2.0))
        self.assertEqual(range_infos, {
            'last': '12:45:00',
            'first': '11:24:00'
        })

        IvyUnBindMsg(s_id)
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))

    def test_cancel(self):
        """Test the CancelLastOrder command"""
        f_id = 10001
        t_heading = 180

        i_trajectory = self.__parse_traj(self.get_trajectory(f_id))
        IvySendMsg("SetClock Time=12:09:00")
        time.sleep(0.1)
        IvySendMsg("AircraftHeading Flight={0} To={1}".format(f_id, t_heading))
        time.sleep(0.1)
        IvySendMsg("CancelLastOrder Flight={0}".format(f_id))
        trajectory = self.__parse_traj(self.get_trajectory(f_id))
        for idx, cone in enumerate(i_trajectory):
            self.assertEqual(cone, trajectory[idx])


