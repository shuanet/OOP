
Clock
-----

**ClockStop**
    Message from an application to freeze the simulation clock::

        ClockStop

**ClockStart**
    Message sent by an application to restart the simulation clock (with the same parameters as before the stop)::

        ClockStart

**ClockBackward**
    Message sent by an application to set the clock to reverse mode (the current speed is unchanged)::

        ClockBackward

**ClockForward**
    Message sent by an application to set the clock to normal sense (The current speed is unchanged)::

        ClockForward

**SetClock**
    Sets the current simulation time (The clock may or may not be on) or the speed of the clock::

        SetClock Time=18:45:12
        SetClock Rate=2.5

**GetClockDatas**
    Request to PyRejeu to give the current parameters of the clock::

        GetClockDatas

    PyRejeu answers with the following message::

        ClockDatas Time=18:46:34 Rate=1.0 Bs=0 Stop=1

    The answer parameters are the same as for :ref:`ClockEvent <ClockEvent>` event, with the extra *Stop* parameter:
     * 0: the clock is running
     * 1: the clock is stopped
