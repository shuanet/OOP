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

from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from pyrejeu.db.models import Base


class DatabaseConnection(object):
    """
    Class used to connect to the Database
    """
    Session = scoped_session(sessionmaker())

    def __init__(self, file_path=None, **kwargs):
        if file_path is None:
            file_path = ":memory:"
            kwargs.update({
                "connect_args": {'check_same_thread': False},
                "poolclass": StaticPool
            })
        self.engine = create_engine('sqlite:///%s' % file_path,
                                    echo=False, **kwargs)
        # configure scoped session
        self.Session.configure(bind=self.engine)
        # create database
        Base.metadata.create_all(self.engine)

    def clear_all_tables(self):
        Base.metadata.clear()

    def get_engine(self):
        """
        Return the active sqlalchemy engine
        """
        return self.engine

    def get_session(self):
        """
        Create a sqlalchemy session object to use the ORM

        :return: Session Object
        """
        return self.Session()
