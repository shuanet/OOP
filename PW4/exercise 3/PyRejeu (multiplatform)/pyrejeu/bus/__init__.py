# -*- coding: utf-8 -*-
# PyRejeu, an air traffic replay tool
# Copyright (C) 2017 Mickael Royer <mickael.royer@enac.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import re
import logging


def init_bus_module(options):
    options.bus_id = options.bus_id.strip()
    # Ivy bus
    m = re.match(r"^ivy://(?P<host>[A-Za-z\d\.-_]+):(?P<port>[0-9]+)$",
                 options.bus_id)
    if m is not None:
        try:
            from pyrejeu.bus.ivy_bus import IvyBus
        except ImportError:
            logging.error("Unable to connect to ivy bus: "
                          "ivy-python is not installed")
        else:
            log_level = options.verbose and logging.INFO or logging.ERROR
            ivy_bus = "{0}:{1}".format(m.group("host"), m.group("port"))
            return IvyBus(ivy_bus, options.app_name, log_level)

    # ZMQ bus
    m = re.match(r"^zmq://(?P<host>[A-Za-z\d\.-_\*]+)"
                 ":(?P<r_p>[0-9]+):(?P<e_p>[0-9]+)$", options.bus_id)
    if m is not None:
        try:
            from pyrejeu.bus.zmq_bus import ZmqBus
        except ImportError:
            logging.error("Unable to use to zmq library: "
                          "pyzmq is not installed")
        else:
            return ZmqBus(*m.group("host", "r_p", "e_p"))

    # AMQP bus
    m = re.match(r"^amqp://(?P<host>[A-Za-z\d\.-_\*]+)"
                 ":(?P<r_p>[0-9]+)$", options.bus_id)
    if m is not None:
        try:
            from pyrejeu.bus.amqp_bus import AmqpBus
        except ImportError:
            logging.error("Unable to use to ampq library: "
                          "python-pika is not installed")
        else:
            return AmqpBus(options.bus_id)

    if m is None:
        logging.error("Bus %s is not supported", options.bus_id)
    return None
