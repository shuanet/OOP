
Flight Informations Requests
----------------------------

**GetTrajectory**
    Message to request PyRejeu to provide all the known points of a registered trajectory (or possibly modified following pilot orders)::

        GetTrajectory MsgName=MyTraj Flight=54 From=Now

    **Parameters**:
     * **MsgName**: string used to identify the answer.
     * **Flight**: the flight identifier
     * **From**: The starting time for the trajectory, can take the values:
        * *Now* to take the current time
        * *Origin* to get all the trajectory
        * *HH:MM:SS* to specify a custom time

    PyRejeu answers with the following messages when the flight exists::

        Trajectory MyTraj Slice=95.25 -140.56 10:20:01 300 94.83 -139.98 10:20:09 300 ...
        Trajectory MyTraj Slice=......
        Trajectory MyTraj Slice=...... <= possibly less infos
        Trajectory MyTraj EndSlice

**GetTrack**
    Message to request PyRejeu to provide the full track of a registered flight

        GetTrack MsgName=MyTrack Flight=54 From=origin

    This command takes the same parameters than *GetTrajectory*. PyRejeu answers with the following messages when the flight exists::

        Track MyTrack Slice=10:20:01 95.25 -140.56 300 94 290 0 0 10:20:09 .... ...
        Track MyTrack Slice=......
        Track MyTrack Slice=...... <= possibly less infos
        Track MyTrack EndSlice

**GetPln**
    Message to ask PyRejeu to provide the flight plan as it was realized and recorded in the file COURAGE::

        GetPln MsgName=Pln54ForMe Flight=54 From=OLRAK

    This command takes the same parameters than *GetTrajectory*. PyRejeu answers with the following messages when the flight exists::

        Pln Pln54ForMe Flight=54 Time=07:10:12 CallSign=CRX766 AircraftType=SB20 Ssr=6744 Speed=360 Rfl=190 Dep=LFSB Arr=LFBO Rvsm=TRUE Tcas=TA_ONLY Adsb=NO DLink=NO List=OLRAK V 06:53 190 NARAK A 07:02 190 NOPTA A 07:09 190

**GetRange**
    Message sent by an application to request the time interval of a flight (or ALL flight) and its visibility::

        GetRange MsgName=MyRange123 Flight=123
        GetRange MsgName=MySimuRange Flight=ALL

    **Parameters**:
     * **MsgName**: string used to identify the answer.
     * **Flight**: the flight identifier or *ALL* to return the global range.

    PyRejeu answers with the following message when the flight exists::

        Range MyRange123 FirstTime=06:08:14 LastTime=07:26:40 Visible=yes

**GetPosition**
    A message issued by an application to request the position of a flight at a given time::

        GetPosition MsgName=pos45 Flight=45 Time=13:06:35

    **Parameters**:
     * **MsgName**: string used to identify the answer.
     * **Flight**: the flight identifier
     * **Time**: the specified time
        * *Now* to take the current time
        * *HH:MM:SS* to specify a custom time

    PyRejeu answers with the following message when the flight exists::

        Position pos45 Flight=45 CallSign=LB114JQ Ssr=0452 Sector=SL Layers=F,I X=87.00 Y=-128.88 Vx=-197 Vy=265 Afl=195 Rate=2098 Heading=323 GroundSpeed=330 Tendency=1 Time=13:06:38
