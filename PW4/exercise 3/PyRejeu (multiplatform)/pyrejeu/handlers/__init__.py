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

import os
import glob
import logging


def set_handlers(bus, db_conn, clock):
    base = os.path.dirname(__file__)
    base_import = "pyrejeu.handlers"
    handlers = []

    modules = [os.path.basename(f[:-3]) \
               for f in glob.glob(os.path.join(base, "[!_]*.py"))]
    for m in modules:
        mod = __import__(base_import + "." + m, {}, {}, base)
        try:
            handler = mod.handler(bus, db_conn, clock)
            handler.subscribe()
            handlers.append(handler)
            logging.info("Init handler %s" % handler.NAME)
        except AttributeError:
            continue
    return handlers
