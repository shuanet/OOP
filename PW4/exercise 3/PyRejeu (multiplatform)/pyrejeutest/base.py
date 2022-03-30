# -*- coding: utf-8 -*-

import re
import unittest
import time
import uuid
from threading import Event, Thread
from queue import Queue, Empty
from ivy.std_api import IvySendMsg, IvyBindMsg, IvyUnBindMsg
from pyrejeutest.utils.server import TestServer
from pyrejeutest.utils.databuilder import TestData
from pyrejeutest.utils.jsonrpc import JSONRPCRequest, parse_response
from pyrejeutest.utils.jsonrpc import parse_event

IVY_BUS_ID = "127.255.255.255:2010"
ZMQ_BUS_ID = "*:6000:6001"
AMQP_BUS_ID = "localhost:5672"


class AmqpPyRejeuTest(unittest.TestCase):
    RPC_QUEUE = "pyrejeu_rpc_queue"
    EVT_EXCHANGE = "pyrejeu_event_exchange"

    @classmethod
    def setUpClass(cls):
        bus_url = "amqp://%s" % AMQP_BUS_ID
        cls.test_data = TestData()
        cls.test_server = TestServer()
        cls.test_server.start("-b %s" % bus_url)

        # connect to server
        import pika
        cls.connection = pika.BlockingConnection(pika.URLParameters(bus_url))
        cls.channel = cls.connection.channel()
        # define rpc queue
        result = cls.channel.queue_declare(exclusive=True)
        cls.callback_queue = result.method.queue
        # define event queue
        result = cls.channel.queue_declare(exclusive=True)
        cls.evt_queue = result.method.queue
        cls.channel.exchange_declare(exchange=cls.EVT_EXCHANGE, type='topic')
        cls.channel.queue_bind(exchange=cls.EVT_EXCHANGE,
                               queue=cls.evt_queue,
                               routing_key="evt.*")

    @classmethod
    def tearDownClass(cls):
        time.sleep(0.1)
        cls.connection.close()
        cls.test_server.stop()

    def setUp(self):
        self.corr_id = None
        self.response = None
        self.rpc_tag = self.channel.basic_consume(self.on_response,
                                                  no_ack=True,
                                                  queue=self.callback_queue)
        # receive events
        self.events = Queue(maxsize=1000)
        self.evt_tag = self.channel.basic_consume(self.on_event, no_ack=True,
                                                  queue=self.evt_queue)
        # start thread to cosumme messages
        self.running = True
        self.thread = Thread(target=self.start_consuming)
        self.thread.start()

    def tearDown(self):
        self.channel.basic_cancel(self.evt_tag)
        self.channel.basic_cancel(self.rpc_tag)
        if self.thread is not None:
            self.running = False
            self.thread.join()

    def start_consuming(self):
        while self.running:
            self.connection.process_data_events(time_limit=0.1)

    def on_event(self, ch, method, props, body):
        self.events.put(parse_event(body))

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def send_command(self, cmd_name, args={}):
        import pika
        self.response = None
        self.corr_id = str(uuid.uuid4())

        request = JSONRPCRequest(cmd_name, args)
        self.channel.basic_publish(exchange='',
                                   routing_key='pyrejeu_rpc_queue',
                                   properties=pika.BasicProperties(
                                        reply_to=self.callback_queue,
                                        correlation_id=self.corr_id,
                                   ),
                                   body=request.dump())
        while self.response is None:
            time.sleep(0.1)

        return parse_response(self.response)


class ZmqPyRejeuTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_data = TestData()
        cls.test_server = TestServer()
        cls.test_server.start("-b zmq://%s" % ZMQ_BUS_ID)

        # connect to server
        import zmq
        b_id = ZMQ_BUS_ID.split(":")
        cls.client = zmq.Context().socket(zmq.REQ)
        cls.client.connect("tcp://{0}:{1}".format("localhost", b_id[1]))

    @classmethod
    def tearDownClass(cls):
        time.sleep(0.1)
        cls.client.close()
        cls.test_server.stop()

    def setUp(self):
        self.evt_queue = Queue()
        self.evt_thread = None
        self.evt_recording = False

    def tearDown(self):
        if self.evt_thread is not None:
            self.evt_recording = False
            self.evt_thread.join()

    def send_command(self, cmd_name, args={}):
        cmd = JSONRPCRequest(cmd_name, args)
        self.client.send(cmd.dump())
        return parse_response(self.client.recv())

    def record_events(self):
        if not self.evt_recording:
            self.evt_recording = True
            self.evt_thread = Thread(target=self.__receive_events)
            self.evt_thread.start()

    def __receive_events(self):
        import zmq
        b_id = ZMQ_BUS_ID.split(":")
        evt_socket = zmq.Context().socket(zmq.SUB)
        evt_socket.connect("tcp://localhost:%s" % b_id[2])
        # subscribe to all events
        evt_socket.setsockopt(zmq.SUBSCRIBE, b'')

        poller = zmq.Poller()
        poller.register(evt_socket, zmq.POLLIN)
        while self.evt_recording:
            evts = dict(poller.poll(timeout=0.1))
            if evt_socket in evts:
                evt = parse_event(evt_socket.recv())
                self.evt_queue.put(evt)
        evt_socket.close()

    def get_event(self):
        try:
            return self.evt_queue.get(timeout=1.0)
        except Empty:
            return None

    def get_all_beacons(self, t="All"):
        """
        Get all the beacons known by PyRejeu
        :return: the list of beacons
        """
        return self.send_command("GetAllBeacons", {"Type": t})["result"]


class IvyPyRejeuTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_data = TestData()
        cls.test_server = TestServer()
        cls.test_server.start("-b ivy://%s" % IVY_BUS_ID)

    @classmethod
    def tearDownClass(cls):
        time.sleep(0.1)
        cls.test_server.stop()

    def setUp(self):
        self.__event = Event()
        self.__pln = None
        self.__trajectory = None
        self.__tracks = None
        self.__clock_datas = None
        self.__beacons = None

    def __parse_beacons(self, beacons):
        beacons = re.findall(r"\S+ \S+ \S+", beacons)
        beacons = [b.split() for b in beacons]
        return [{
            "pos_x": float(x),
            "pos_y": float(y),
            "name": name
        } for name, x, y in beacons]

    def __on_beacon_msg(self, *largs):
        self.__beacons += " " + largs[1]

    def get_all_beacons(self, t="All"):
        """
        Get all the beacons known by PyRejeu
        :return: the list of beacons
        """
        msg_id = self.test_data.get_random_string()
        self.__beacons = ""
        self.__event.clear()

        # bind to PyRejeu answers before sending the command
        b_id = IvyBindMsg(self.__on_beacon_msg,
                          "AllBeacons {0} Slice=(.*)".format(msg_id))
        end_b_id = IvyBindMsg(lambda *l: self.__event.set(),
                              "AllBeacons {0} EndSlice".format(msg_id))
        IvySendMsg("GetAllBeacons MsgName={0} Type={1}".format(msg_id, t))
        # validate the answer of PyRejeu
        self.assertTrue(self.__event.wait(timeout=3.0),
                        "Beacons are not received")
        IvyUnBindMsg(b_id)
        IvyUnBindMsg(end_b_id)
        return self.__parse_beacons(self.__beacons)

    def get_beacons(self, b_list, null_coord="0.0"):
        """
        Get informations about the beacon identified by its name
        :param b_name: beacon name
        :return: beacon informations
        """
        msg_id = self.test_data.get_random_string()
        self.__beacons = ""
        self.__event.clear()

        def on_beacons_infos(agent, data):
            self.__beacons = data
            self.__event.set()

        # bind to PyRejeu answers before sending the command
        b_id = IvyBindMsg(on_beacons_infos,
                          "BeaconsInfos {0} List=(.*)".format(msg_id))
        IvySendMsg("GetBeaconsInfos MsgName={0} NullCoord={2} "
                   "List={1}".format(msg_id, " ".join(b_list), null_coord))
        # validate the answer of PyRejeu
        self.assertTrue(self.__event.wait(timeout=3.0),
                        "Beacon infos are not received")
        IvyUnBindMsg(b_id)
        return self.__parse_beacons(self.__beacons)

    def __on_trajectory_msg(self, *largs):
        self.__trajectory += " " + largs[1]

    def get_trajectory(self, flight_id):
        """
        Get the trajectory of a flight sending a command to PyRejeu

        :param flight_id: the flight identifier
        :return: the trajectory of this flight
        """
        msg_id = self.test_data.get_random_string()
        self.__trajectory, t_event = "", Event()

        # bind to PyRejeu answers before sending the command
        t_bind_id = IvyBindMsg(self.__on_trajectory_msg,
                               "Trajectory {0} Slice=(.*)".format(msg_id))
        end_bind_id = IvyBindMsg(lambda *l: t_event.set(),
                                 "Trajectory {0} EndSlice".format(msg_id))
        IvySendMsg("GetTrajectory MsgName={0} "
                   "Flight={1} From=origin".format(msg_id, flight_id))
        # validate the answer of PyRejeu
        self.assertTrue(t_event.wait(timeout=3.0),
                        "Trajectory for flight {0} endSlice "
                        "not received".format(flight_id))
        # unbind to trajectory messages
        for b_id in (end_bind_id, t_bind_id):
            IvyUnBindMsg(b_id)
        return self.__trajectory

    def __parse_track(self, track):
        t_points = re.findall(r"\S+ \S+ \S+ \S+ \S+ \S+ \S+ \S+", track)
        t_points = [t.split() for t in t_points]
        return [{
            "pos_x": float(x),
            "pos_y": float(y),
            "vit_x": float(vx),
            "vit_y": float(vy),
            "rate": float(rate),
            "fl": int(fl),
            "tendency": int(tendency),
            "hour": hour,
        } for hour, x, y, vx, vy, fl, rate, tendency in t_points]

    def __on_track_msg(self, agent, data):
        self.__tracks += " " + data

    def get_track(self, flight_id):
        """
        Get the full track of a flight sending a command to PyRejeu

        :param flight_id: the flight identifier
        :return: the trajectory of this flight
        """
        msg_id = self.test_data.get_random_string()
        self.__tracks, t_event = "", Event()

        # bind to PyRejeu answers before sending the command
        t_bind_id = IvyBindMsg(self.__on_track_msg,
                               "Track {0} Slice=(.*)".format(msg_id))
        end_bind_id = IvyBindMsg(lambda *l: t_event.set(),
                                 "Track {0} EndSlice".format(msg_id))
        IvySendMsg("GetTrack MsgName={0} "
                   "Flight={1} From=origin".format(msg_id, flight_id))
        # validate the answer of PyRejeu
        self.assertTrue(t_event.wait(timeout=3.0),
                        "Track for flight {0} endSlice "
                        "not received".format(flight_id))
        # unbind to trajectory messages
        for b_id in (end_bind_id, t_bind_id):
            IvyUnBindMsg(b_id)
        return self.__parse_track(self.__tracks)

    def __on_pln_msg(self, *larg):
        datas = larg[1].split(" ")
        datas = [d.split("=") for d in datas]
        self.__pln = dict(datas)
        self.__pln["List"] = larg[2]
        self.__event.set()

    def get_pln(self, flight_id, from_type="origin"):
        """
        Retrieve the flight plan from PyRejeu

        :param flight_id: the flight identifier
        :return: the fpl of this flight
        """
        msg_id = self.test_data.get_random_string()
        self.__pln = ""
        self.__event.clear()

        # bind to PyRejeu answers before sending the command
        b_id = IvyBindMsg(self.__on_pln_msg,
                          "Pln {0} (.*) List=(.*)".format(msg_id))
        IvySendMsg("GetPln MsgName={0} Flight={1} "
                   "From={2}".format(msg_id, flight_id, from_type))
        # validate the answer of PyRejeu
        self.assertTrue(self.__event.wait(timeout=3.0),
                        "Pln for flight {0} not received".format(flight_id))
        IvyUnBindMsg(b_id)
        return self.__pln

    def __on_clock_datas_msg(self, *larg):
        self.__clock_datas = {
            "Time": larg[1],
            "Rate": larg[2],
            "Bs": larg[3],
            "Stop": larg[4]
        }
        self.__event.set()

    def get_clock_datas(self):
        """
        Retrieve the clock state from PyRejeu
        """
        self.__clock_datas = {}
        self.__event.clear()

        b_id = IvyBindMsg(self.__on_clock_datas_msg,
                          "ClockDatas Time=(\S+) Rate=(\S+) "
                          "Bs=(\S+) Stop=(\S+)")
        IvySendMsg("GetClockDatas")
        self.assertTrue(self.__event.wait(timeout=3.0),
                        "ClockDatas msg not received")
        IvyUnBindMsg(b_id)
        return self.__clock_datas
