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
import collections
from sqlalchemy import and_, or_, not_
from pyrejeu.db.models import Flight
from pyrejeu.db.models import FlightPlanBeacon

Token = collections.namedtuple('Token', ['type', 'value'])
KEYWORDS_TRANSLATION = {
    "AircraftType": Flight.type,
    "Fl": Flight.fl,
    "CallSign": Flight.callsign,
    "Speed": Flight.v,
    "Arr": Flight.arr,
    "Dep": Flight.dep,
    "Ssr": Flight.ssr,
    "Rvsm": Flight.rvsm,
    "Tcas": Flight.tcas,
    "Adsb": Flight.adsb,
    "Dlink": Flight.dlink,
    "Beacon": FlightPlanBeacon.beacon_name
}
OP_TRANSLATION = {
    "=": "__eq__",
    "<": "__lt__",
    ">": "__gt__",
}
BIN_OP_TRANSLATION = {
    "and": and_,
    "or": or_,
    "not": not_,
}


def tokenize(filter_str):
    k_keys = list(KEYWORDS_TRANSLATION.keys())
    token_specification = [
        ('KEYWORD', r'{0}'.format("|".join(k_keys))),
        ('OPEN_BRACKET',   r'\('),
        ('CLOSE_BRACKET',   r'\)'),
        ('BINARY_OP',   r'and|or|not'),
        ('PATTERN',   r'[A-Za-z\d\*\?\.]+'),
        ('OP',       r'[=><]'),
        ('SKIP',     r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, filter_str):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError("mismatch for value %s" % value)
        else:
            yield Token(kind, value)


def set_filter(keyword, op, value):
    column = KEYWORDS_TRANSLATION[keyword]
    if op == "=" and re.search(r".*[\?\*].*", value) is not None:
        value = value.replace("?", "_")
        value = value.replace("*", "%")
        sql_op = column.like
    else:
        sql_op = getattr(column, OP_TRANSLATION[op])
    return sql_op(value)


def translate_filter(filter_str):
    b_level = 0
    bin_op = {0: {"not": False, "comb": None}}
    temp_filters = {0: []}
    current_type = None
    current_op = None

    for token in tokenize(filter_str):
        if token.type == "OPEN_BRACKET":
            b_level += 1
            temp_filters[b_level] = []
            bin_op[b_level] = {"not": False, "comb": None}
        elif token.type == "PATTERN":
            if current_op is None or current_type is None:
                raise RuntimeError("String value found before operator "
                                   "and keyword")
            f = set_filter(current_type, current_op, token.value)
            if bin_op[b_level]["not"]:
                f = not_(f)
                bin_op[b_level]["not"] = False
            temp_filters[b_level].append(f)
            current_op, current_type = None, None
        elif token.type == "KEYWORD":
            current_type = token.value
        elif token.type == "OP":
            if current_op is not None:
                raise RuntimeError("Two successive operators")
            current_op = token.value
        elif token.type == "BINARY_OP":
            if token.value == "not":
                bin_op[b_level]["not"] = True
            elif bin_op[b_level]["comb"] is not None \
                    and bin_op[b_level]["comb"] != token.value:
                raise RuntimeError("Multiple binary operator inside bracket")
            else:
                bin_op[b_level]["comb"] = token.value
        elif token.type == "CLOSE_BRACKET" and bin_op[b_level] is not None:
            if b_level == 0:
                raise RuntimeError("Unexpected close bracket")
            sql_op = BIN_OP_TRANSLATION[bin_op[b_level]["comb"]]
            f = sql_op(*temp_filters[b_level])
            if bin_op[b_level-1]["not"]:
                f = not_(f)
                bin_op[b_level-1]["not"] = False
            temp_filters[b_level-1].append(f)
            bin_op[b_level] = {"not": False, "comb": None}
            temp_filters[b_level] = []
            b_level -= 1

    if b_level != 0:
        raise RuntimeError("Problem with brackets")

    if bin_op[0]["comb"] is not None:
        sql_op = BIN_OP_TRANSLATION[bin_op[0]["comb"]]
        return sql_op(*temp_filters[0])
    elif len(temp_filters[0]) != 1:
        raise RuntimeError("multiple filter without operator")
    return temp_filters[0][0]
