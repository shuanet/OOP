
Database Requests
-----------------

**GetAllBeacons**
    Ask PyRejeu to provide informations for all known beacons::

        GetAllBeacons MsgName=X123 Type=All

    *Type* can take two values:
     * **Pilot**: Only beacons known by pilots are returned.
     * **All**: All the beacons are returned.

    PyRejeu answers with the following messages::

        AllBeacons X123 Slice=LAULY 147.88 72.38 LEPRA 375.25 -190.13 MARRI .. .
        AllBeacons X123 Slice=...... ..... ...... ..... ...... ..... .. .. .
        AllBeacons X123 Slice=...... <= possibly less infos
        AllBeacons X123 EndSlice

**GetBeaconsInfos**
    Ask PyRejeu to provide inforations for the beacons whose names are provided in List::

        GetBeaconsInfos MsgName=X123 NullCoord=N/A List=LFBO TOU XYZ AFRIC

    PyRejeu answers with the following message::

        BeaconsInfos X123 List=LFBO 58.00 -209.38 TOU 57.13 -198.38 XYZ N/A N/A AFRIC 124.25 -191.63

**SetNewBeacons**
    Ask PyRejeu to take into account beacons given in the *List* parameter::

        SetNewBeacons List=LVM 10.0 -45.76 XMFF 23.78 -65.45 .....

    **Parameters**
     * **List**: contains triplets {Name X Y} for each beacon

    If the command is correctly formatted, PyRejeu sends a :ref:`BeaconUpdateEvent <BeaconUpdateEvent>` event.

**GetCurrentFlights**
    Ask PyRejeu to provide all the flights existing at the given time::

        GetCurrentFlights MsgName=ForMe Time=Now

    **Parameters**:
     * **MsgName**: string used to identify the answer.
     * **Time**: time, PyRejeu supports the format HH:MM:SS, HH:MM or the value Now (meaning the current time).

    PyRejeu answers with the following message::

        CurrentFlights ForMe Time=10:16:35 List=45 876 13 6543 568 90 146

    *List* field contains the ids of flights which fullfill the following conditions:
     * It is enabled (meaning not concern by the Discard command)
     * First known cone < Given time < Last known cone

**GetDataBaseInfos**
    Ask PyRejeu to provide flights matching with the filter given in the Cond field

        GetDataBaseInfos MsgName=X234 Cond=(CallSign=AF*) and (Dep=LFBO) Select=CallSign,Arr

    **Parameters**:
     * **MsgName**: string used to identify the answer.
     * **Cond**: flight filter.
     * **Select (Optionnal)**: list of informations to return for each selected flight (after the id)

    PyRejeu answers with the following message::

        DataBaseInfos X234 Nb=7 List=12,AF123KQ,LFPG 87,AFR3011,LEVC 79,AF234GH,LFMT .......

.. warning ::

    Currently, PyRejeu has some limitations, compared to the legacy rejeu application:
     * *Passing_Through* parameter is not supported.
     * Inside filter, *ExistIn* field is not supported.
     * In Select parameter, *FirstTime* and *LastTime* fields are not supported.
