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

import logging
from pyrejeu.format import Event
from pyrejeu.utils import log_traceback
from pyrejeu.db.models import Flight
from pyrejeu.format import RpcError, RpcAck


__version__ = "0.2.0"


def rpc_decorator(require_flight=False, commit=False):
    def rpc_decorator_func(func):
        def new_func(self, msg_id, *args, **kwargs):
            session = self.db_conn.get_session()
            if require_flight:
                flight_id = args[0]
                flight = session.query(Flight).get(flight_id)
                if flight is None:
                    err = "Unable to find flight {0}".format(flight_id)
                    self.bus.rpc_answer(self.error(msg_id, err))
                    return
                args = [flight] + list(args[1:])
            try:
                answer = func(self, session, msg_id, *args, **kwargs)
                if commit and not isinstance(answer, RpcError):
                    session.commit()
            except Exception:
                session.rollback()
                logging.error("An exception occurs in func %s", func)
                logging.error("See traceback for details")
                log_traceback()
            else:
                answer = answer or RpcAck(msg_id)
                self.bus.rpc_answer(answer)
            finally:
                session.close()

        new_func.__name__ = func.__name__
        new_func.__doc__ = func.__doc__
        return new_func

    return rpc_decorator_func


class PyRejeuBaseObject(object):

    def __init__(self, bus, db_conn):
        self.bus = bus
        self.db_conn = db_conn

    def set_subscriptions(self, subscriptions):
        for sub in subscriptions:
            self.bus.subscribe(sub)

    def send_event(self, evt_name, attrs):
        self.bus.publish_event(Event(evt_name, attrs))

    def error(self, msg_name, err_msg):
        logging.error(err_msg)
        return RpcError(msg_name, err_msg)


class PyRejeuException(Exception):
    pass
