#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PyRejeu, an air traffic replay tool
# Copyright (C) 2017 Mickael Royer <mickael.royer@enac.fr>

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

"""
This is the test suite launcher :
    * Without arguments, it runs the whole test suite.
    * It accepts a list of arguments which can be :
        - a test module name without the 'test_' prefix.
          e.g. : ./tests.py utils
        - a test module name without the 'test_' prefix, a slash, and a test
          name in unittest dotted notation (See the documentation of
          loadTestsFromName at
          http://docs.python.org/lib/testloader-objects.html)
          e.g. : ./tests.py utils/UtilsTest.test_sec_to_str
    * If the fist argument is 'list', list all the possibles tests that can be
      combined on the command line restricted by the same arguments.
      e.g. : ./tests.py list utils importations
      would list all the tests that are to be run from those test modules.
"""

from optparse import OptionParser
import os
import glob
from ivy.std_api import IvyInit, IvyStart, IvyStop
import logging
import time
import unittest
import pyrejeutest.base

usage = "usage: %prog [options] [tests-list]"
parser = OptionParser(usage=usage)
parser.set_defaults(ivy_bus_id="127.255.255.255:2010")
parser.add_option('-b', '--bus', type='string', dest='ivy_bus_id',
                  help="Ivy bus id (format @IP:port "
                       "default to 127.255.255.255:2010)")
(options, myargs) = parser.parse_args()
# set bus id to launch server
pyrejeutest.base.IVY_BUS_ID = options.ivy_bus_id

TEST_NAMESPACE = 'pyrejeutest'
test_suites_dir = os.path.join(os.path.dirname(__file__), TEST_NAMESPACE)


# Workaround for __import__ behavior, see
# http://docs.python.org/lib/built-in-funcs.html
def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def get_testfile_from_id(id):
    return os.path.join(test_suites_dir, "test_%s.py" % id)


def get_id_from_module(module):
    return module.__name__[len(TEST_NAMESPACE+'.'+'test_'):]


def get_all_tests():
    return [(x, None) for x in glob.glob(get_testfile_from_id("*"))]


tests_to_run = None
list_only = False
args = None
if len(myargs) > 0:
    if myargs[0] == 'list':
        list_only = True
        args = myargs[1:]
    else:
        args = myargs

if args:
    tests_to_consider = []
    for test_id in args:
        try:
            test_module, test_name = test_id.split('/')
        except ValueError:
            test_module = test_id
            test_name = None

        tests_to_consider.append((get_testfile_from_id(test_module),
                                  test_name))
else:
    tests_to_consider = get_all_tests()


def get_test_suite(test_module, test_name=None):
    t_suite = None
    if test_name:
        t_suite = unittest.defaultTestLoader.loadTestsFromName(test_name,
                                                               test_module)
    else:
        t_suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
    return t_suite


def get_module_and_name(test_id):
    fn, test_name = test_id
    module_path = '.'.join([TEST_NAMESPACE, os.path.basename(fn[:-3])])
    test_module = my_import(module_path)
    return test_module, test_name


def print_tests(class_name, test_name=None):
    if class_name.startswith('Test'):
        has_tests = False
        for fun_name in dir(getattr(test_module, class_name)):
            if fun_name.startswith('test')\
                    and (not test_name or fun_name == test_name):
                has_tests = True
                print("%s/%s.%s" % (get_id_from_module(test_module),
                                    class_name, fun_name))
        if has_tests:
            print("%s/%s" % (get_id_from_module(test_module),
                             class_name))


if list_only:
    for test_id in tests_to_consider:
        test_module, test_name = get_module_and_name(test_id)
        if test_name:
            splitted_test_name = test_name.split('.')
            if len(splitted_test_name) > 1:
                class_name, test_name = splitted_test_name
            else:
                class_name, test_name = splitted_test_name[0], None
            print_tests(class_name, test_name)
        else:
            for class_name in dir(test_module):
                print_tests(class_name)
else:
    suitelist = []
    runner = unittest.TextTestRunner(verbosity=2)
    for test_id in tests_to_consider:
        test_module, test_name = get_module_and_name(test_id)
        suitelist.append(get_test_suite(test_module, test_name))

    # start ivy server before launching the test suite
    def null_cb(*a):
        pass

    ivy_logger = logging.getLogger('Ivy')
    ivy_logger.setLevel(logging.ERROR)
    IvyInit("pyrejeutest", "test READY", 0, null_cb, null_cb)
    IvyStart(options.ivy_bus_id)
    # wait that all the threads have been initialised
    time.sleep(0.5)
    runner.run(unittest.TestSuite(suitelist))
    # disconnect from ivy bus
    IvyStop()
