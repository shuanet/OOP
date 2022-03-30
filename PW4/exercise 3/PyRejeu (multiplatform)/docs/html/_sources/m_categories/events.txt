
Events
------

.. _ClockEvent:

**ClockEvent**
    PyRejeu emits periodically this message that gives the current hour of the simulation::

        ClockEvent Time=10:23:45 Rate=3 Bs=0

    **Parameters**:
     * *Time*: the current time (HH:MM:SS format)
     * *Rate*: the current clock speed (Rate < 0 when the clock is in reverse mode)
     * *Bs*: Big Speed mode (o: disabled, 1: enabled)

.. note ::

    Currently, Big Speed mode is not supported by PyRejeu

**TrackMovedEvent**
    Message emitted by PyRejeu to indicate a new position for a flight::

        TrackMovedEvent Flight=324 CallSign=LB114JQ Ssr=0452 Sector=SL Layers=F,I X=87.00 Y=-128.88 Vx=-197 Vy=265 Afl=195 Rate=2098 Heading=323 GroundSpeed=330 Tendency=1 Time=12:08:32

**TrackDiedEvent**
    This message indicates the end of a track::

        TrackDiedEvent Flight=654

**PlnEvent**
    PyRejeu emits this message in two cases:
    * Before the first message of position
    * When the flight plan has been modified
    *Example*::

        PlnEvent Flight=55 Time=07:00:12 CallSign=CRX766 AircraftType=SB20 Ssr=6744 Speed=360 Rfl=190 Dep=LFSB Arr=LFBO Rvsm=TRUE Tcas=TA_ONLY Adsb=NO DLink=NO List=OLRAK V 06:53 190 NARAK A 07:02 190 NOPTA A 07:09 190

**TrajectoryUpdateEvent**
    This message is emitted when the trajectory of a flight has been updated::

        TrajectoryUpdateEvent Flight=7040

**ReportEvent**
    This message is emitted by PyRejeu after a pilot order to indicate the result of the order::

        ReportEvent IIPP1 Result=ERROR Info=STD_TRACKS.UNKNOWN_TRACK Order=AircraftFollowTrack|6371|Star|Meden18
        ReportEvent Digipilot Result=OK Info=284 Order=AircraftDirect|6841|BTZ

**FileReadEvent**
    This event is emitted by PyRejeu when it finishes to read data file::

        FileReadEvent Type=REJEU Name=traffic_file.rej StartTime=07:10:05 EndTime=12:45:07

    *StartTime* and *EndTime* fields indicate the time of the first cone and the last known cone in the newly read file, respectively.

.. note ::

    Currently, *REJEU* is the only file type supported by PyRejeu

.. _BeaconUpdateEvent:

**BeaconUpdateEvent**
    This event is sent after a SetNewBeacons command::

        BeaconUpdateEvent List=LVM 10.0 -45.76 XMFF 23.78 -65.45
