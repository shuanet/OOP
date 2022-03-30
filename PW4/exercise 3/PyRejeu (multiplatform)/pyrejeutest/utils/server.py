# -*- coding: utf-8 -*-
"""
Tools to launch a rejeu in background
"""
import os
import sys
import subprocess
import time
import shlex
from pyrejeutest.utils.databuilder import TestData


class TestServer(object):
    """Implements a pyrejeu server ready for testing."""
    db_file = "/tmp/rejeu.db"
    log_file = "/tmp/pyrejeu_test.log"

    def __init__(self):
        self.test_data = TestData()
        self.serverExecRelPath = 'pyrejeu.py'
        self.srcpath = self.findSrcPath()
        self.log_hd = None
        self.__serverProcess = None

    def findSrcPath(self):
        # Get the server executable path, assuming it is names
        # pyrejeu.py in a subdirectory of $PYTHONPATH
        absPath = ''
        notFound = True
        sysPathIterator = iter(sys.path)
        while notFound:
            absPath = next(sysPathIterator)
            serverScriptPath = os.path.join(absPath, self.serverExecRelPath)
            if os.path.exists(serverScriptPath):
                notFound = False

        if notFound:
            raise Exception('Cannot find server executable')

        return os.path.abspath(absPath)

    def start(self, options):
        for f_path in (self.db_file, self.log_file):
            if os.path.isfile(f_path):
                os.unlink(f_path)

        serverExec = os.path.join(self.srcpath, self.serverExecRelPath)
        if not os.access(serverExec, os.X_OK):
            sys.exit("The test server executable '%s' is not executable."
                     % serverExec)

        cmd_line = "{0} {1} {2}".format(os.path.realpath(serverExec),
                                        options,
                                        self.test_data.get_trafic_data_file())
        env = {
            "PYTHONPATH": self.srcpath,
            "PATH": os.getenv('PATH'),
            "LANG": os.getenv('LANG')
        }
        self.log_hd = open(self.log_file, "a")
        self.__serverProcess = subprocess.Popen(shlex.split(cmd_line),
                                                env=env,
                                                stderr=self.log_hd,
                                                stdout=sys.stdout.fileno(),
                                                close_fds=True)
        time.sleep(2.0)

    def stop(self):
        if self.__serverProcess is not None:
            self.__serverProcess.terminate()

            # Wait for the process to finish
            self.__serverProcess.wait()
            self.__serverProcess = None
