#!/usr/bin/env python3
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
import shutil
import re
import sys
import distutils.sysconfig
import distutils.command.build_scripts
from distutils.command.clean import clean as distutils_clean
from distutils.core import setup
from stat import ST_MODE
import pyrejeu


def force_unlink(path):
    try:
        os.unlink(path)
    except OSError:
        pass


def force_rmdir(path):
    try:
        shutil.rmtree(path)
    except OSError:
        pass


class pyrejeu_clean(distutils_clean):

    def run(self):
        distutils_clean.run(self)

        for cmd in self.distribution.command_obj.values():
            if hasattr(cmd, 'clean'):
                cmd.clean()

        force_unlink('MANIFEST')
        force_rmdir('build')
        force_rmdir('docs/doctrees')


# check if Python is called on the first line with this expression
first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')


class build_scripts(distutils.command.build_scripts.build_scripts, object):
    """
    This is mostly distutils copy, it just renames script according
    to platform (.py for Windows, without extension for others)
    """

    def copy_scripts(self):
        """Copy each script listed in 'self.scripts'; if it's marked as a
        Python script in the Unix way (first line matches 'first_line_re',
        ie. starts with "\#!" and contains "python"), then adjust the first
        line to refer to the current Python interpreter as we copy.
        """
        self.mkpath(self.build_dir)
        outfiles = []
        for script in self.scripts:
            adjust = 0
            script = distutils.util.convert_path(script)
            outfile = os.path.join(self.build_dir,
                                   os.path.splitext(os.path.basename(script))[0])
            if sys.platform == 'win32':
                outfile += os.extsep + 'py'
            outfiles.append(outfile)

            if not self.force and \
                    not distutils.dep_util.newer(script, outfile):
                distutils.log.debug("not copying %s (up-to-date)", script)
                continue

            # Always open the file, but ignore failures in dry-run mode --
            # that way, we'll get accurate feedback if we can read the
            # script.
            try:
                f = open(script, "r")
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn("%s is an empty file (skipping)" % script)
                    continue

                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ''

            if adjust:
                distutils.log.info("copying and adjusting %s -> %s", script,
                                   self.build_dir)
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not distutils.sysconfig.python_build:
                        outf.write("#!%s%s\n" %
                                   (os.path.normpath(sys.executable),
                                    post_interp))
                    else:
                        outf.write(
                            "#!%s%s\n" %
                            (os.path.join(
                             distutils.sysconfig.get_config_var("BINDIR"),
                             "python" + distutils.sysconfig.get_config_var("EXE")),
                             post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            else:
                f.close()
                self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    distutils.log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 0o7777
                    newmode = (oldmode | 0o555) & 0o7777
                    if newmode != oldmode:
                        distutils.log.info("changing mode of %s from %o to %o",
                                           file, oldmode, newmode)
                        os.chmod(file, newmode)
    # copy_scripts ()


#
# data files
#
def get_data_files(walking_root, dest_dir):
    data_files = []
    for root, dirs, files in os.walk(walking_root):
        paths = [os.path.join(root, f) for f in files]
        root = root.replace(walking_root, '').strip('/')
        dest_path = os.path.join(dest_dir, root)
        data_files.append((dest_path, paths))
    return data_files


def build_data_files_list():
    data = [
        ('share/doc/pyrejeu', ("README.md",)),
        ]
    data.extend(get_data_files("docs/html", "share/doc/pyrejeu/html"))
    return data


if __name__ == "__main__":
    setup(name="pyrejeu", version=pyrejeu.__version__,
          description="PyRejeu is an application that replay Air Traffic",
          author="Mikael Royer",
          author_email="mickael.royer@enac.fr",
          license="GNU GPL v3",
          scripts=["pyrejeu.py"],
          packages=[
              "pyrejeu",
              "pyrejeu.bus",
              "pyrejeu.db",
              "pyrejeu.handlers"
              ],
          data_files=build_data_files_list(),
          cmdclass={
              'build_scripts': build_scripts,
              "clean": pyrejeu_clean,
          }
    )
