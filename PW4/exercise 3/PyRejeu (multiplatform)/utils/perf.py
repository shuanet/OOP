#!/usr/bin/env python3
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

import sys
import os
import cProfile
import tempfile
import io
import pstats
import contextlib
from optparse import OptionParser
from pyrejeu.db.importations import RejeuImportation
from pyrejeu.db.connection import DatabaseConnection


@contextlib.contextmanager
def profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    # uncomment this to see who's calling what
    # ps.print_callers()
    print(s.getvalue())


if __name__ == "__main__":
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    # database creation
    db_file = tempfile.NamedTemporaryFile(prefix="pyrejeu", suffix=".db")
    db_connection = DatabaseConnection(file_path=db_file.name)

    # file importation
    if len(args) != 1 or not os.path.isfile(args[0]):
        sys.exit("Error: Usage pyrejeu [options] <trace_file>")
    import_obj = RejeuImportation(db_connection)

    with profiled():
        import_obj.import_file(args[0], event=False)
