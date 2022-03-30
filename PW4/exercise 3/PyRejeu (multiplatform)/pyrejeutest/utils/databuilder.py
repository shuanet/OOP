# -*- coding: utf-8 -*-

import os
import random
import time
import string


class TestData(object):
    """This class contains useful functions to generate datas"""

    def __init__(self):
        random.seed(time.time())

    def get_random_string(self, length=5, charset=string.ascii_letters):
        """
        Generate a random string
        :param length: length of the generated string
        :param charset: list of caracter used to build the string
        :return: a random string
        """
        rs = ''.join(random.sample(charset, length - 1))
        return rs

    def get_random_int(self, max_value=10, min_value=1):
        """
        Generate a random integer
        :param max_value: maximum value for the generated integer
        :param min_value: minimum value for the generated integer
        :return: a random integer between min_value and max_value
        """
        return random.randint(min_value, max_value)

    def get_random_element(self, data_list):
        """
        Pick up an element in a list
        :param data_list: the input list
        :return: a element pick up from the data_list
        """
        return random.sample(data_list, 1).pop()

    def get_trafic_data_file(self):
        """
        Get the absolute path for the simple trafic file
        :return: absolute path for the simple trafic file
        """
        path = os.path.dirname(__file__)
        return os.path.join(path, "trafic_file.txt")
