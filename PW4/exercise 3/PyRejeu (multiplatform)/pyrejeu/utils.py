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
"""
This module contains some useful functions used in most of the class
of RejeuTraffic
"""

from numpy import sign
import traceback
import logging
import math


def log_traceback(level="info"):
    """
    Log the last exception that has been raised in the application

    :param string: log level used for this traceback
    """
    log_func = level == "info" and logging.info or logging.error
    log_func("------------------Traceback lines--------------------")
    log_func(traceback.format_exc())
    log_func("-----------------------------------------------------")


def str_to_sec(string):
    """
    Convert a string following the format HH:MM:SS to a number of seconds
    (since 00:00:00)

    :param string: string following the format HH:MM:SS
    :return: the number of seconds since 00:00:00
    """
    (h, m, s) = string.split(':')
    return int(h)*3600 + int(m)*60 + int(s)


def sec_to_str(nb_sec, seconds=True):
    """
    Convert a number of seconds to a string following the format HH:MM[:SS]

    :param nb_sec: number of second since the beginning of the day
    :param seconds: set to True (the default) in order to return the seconds
    :return: string following the format HH:MM[:SS]
    """
    h = nb_sec//3600
    nb_sec -= h*3600
    m = nb_sec // 60
    if seconds:
        s = nb_sec - m*60
        return "%02d:%02d:%02d" % (h, m, s)
    return "%02d:%02d" % (h, m)


def get_gs(x_speed, y_speed):
    """
    Calculate the ground speed of an aircraft based on its speed vector

    :param x_speed: x component of the speed vector
    :param y_speed: y component of the speed vector
    :returns: ground speed of the aircraft
    """
    return math.sqrt(x_speed**2 + y_speed**2)


def get_heading(x_speed, y_speed):
    """
    Calculate the heading of an aircraft based on its speed vector

    :param x_speed: x component of the speed vector
    :param y_speed: y component of the speed vector
    :returns: heading of the aircraft in radian
    """
    if x_speed == 0:
        return y_speed < 0 and 180 or 0
    angle = math.atan(y_speed/x_speed)

    if x_speed > 0:
        return math.degrees(math.pi/2 - angle)
    else:
        return math.degrees(3*math.pi/2 - angle)


def get_heading_to_beacon(cur_cone, beacon):
    """
    Calculate the heading to reach the beacon given as argument

    :param cur_cone: x component of the speed vector
    :param y_speed: y component of the speed vector
    :returns: heading to set in order to reach the beacon
    """
    v_x = beacon["pos_x"] - cur_cone["pos_x"]
    v_y = beacon["pos_y"] - cur_cone["pos_y"]
    return get_heading(v_x, v_y)


def modulo_min_max(value, min_v, max_v):
    """
    Be sure that a value if between a minimum and a maximum

    :param value: the value
    :param min_v: the minimum value
    :param max_v: the maximum value
    :returns: a value between min_v and max_v modulo (max_v-min_v)
    """
    assert(min_v < max_v)
    delta = max_v - min_v
    if value < min_v:
        value += delta
    elif value > max_v:
        value -= delta
    return value


def turn_orientation(c_heading, t_heading):
    """
    Determine the turn orientation to reach the target heading

    :param c_heading: current heading
    :param t_heading: target heading
    :returns: Left or Right according the best turn orientation
    """
    d_heading = modulo_min_max(t_heading-c_heading, -180, 180)
    return d_heading < 0 and "Left" or "Right"


def turn(c_heading, t_heading, rate, inc_time):
    """
    Turn the aircraft based on the current/target heading and the turn rate

    :param c_heading: current heading
    :param t_heading: target heading
    :param rate: turn rate
    :returns: new heading
    """
    new_heading = modulo_min_max(c_heading + inc_time*rate, 0, 360)
    d_heading = modulo_min_max(t_heading-new_heading, -180, 180)
    if sign(d_heading) != sign(rate):
        new_heading = t_heading
    return new_heading


def dist(A, B):
    """
    Return the distance between the point A and B.
    A and B are objects whose have the attributes pos_x ans pos_y

    :returns: the distance between A and B
    """
    return math.sqrt((A["pos_x"] - B["pos_x"])**2
                     + (A["pos_y"] - B["pos_y"])**2)


def min_dist_to_beacon(trajectory, beacon):
    """
    Calculate the minimum distance between a flight trajectory and a beacon

    :param trajectory: a flight trajectory
    :param beacon: the beacon object (with name and position)
    :returns: a tuple (minimum distance, corresponding cone)
    """
    min_cone, min_dist = None, 200000
    for cone in trajectory:
        d = dist(cone, beacon)
        if d < min_dist:
            min_cone = cone
            min_dist = d
    return min_dist, min_cone
