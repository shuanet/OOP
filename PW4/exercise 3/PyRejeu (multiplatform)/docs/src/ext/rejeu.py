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

import json
from docutils import nodes
from sphinx.util.compat import Directive
from docutils.parsers.rst.directives import unchanged


class RejeuCmdDirective(Directive):
    # this enables content in the directive
    has_content = True
    option_spec = dict(desc=unchanged, params=unchanged, example=unchanged)
    required_arguments = 1

    def _format_param(self, p):
        n = nodes.list_item()
        n += nodes.strong(text=p["name"])
        n += nodes.emphasis(text=" - "+p["type"]+" - ")
        n += nodes.Text(p["desc"])
        return n

    def _format_params(self):
        if "params" in self.options:
            params = json.loads(self.options["params"])

            p_node = nodes.paragraph()
            p_node.append(nodes.strong(text="Parameters:"))
            p_list = nodes.bullet_list()
            for p in params:
                p_list.append(self._format_param(p))
            p_node.append(p_list)
            return p_node
        return None

    def _format_example(self):
        e_node = nodes.paragraph()
        e_node.append(nodes.strong(text="Example"))
        e_node.append(nodes.literal_block(text=self.options["example"]))

        return e_node

    def run(self):
        n_list = [
            nodes.paragraph(text=self.options["desc"]),
            self._format_example()
        ]
        p_node = self._format_params()
        if p_node is not None:
            n_list.append(p_node)

        return [
            nodes.topic('',
                        nodes.title(text=self.arguments[0]),
                        *n_list,
                        ids=["rejeu-cmd-sections"])
        ]


def setup(app):
    app.add_directive('rejeu-cmd', RejeuCmdDirective)

    return {'version': '0.1'}   # identifies the version of our extension