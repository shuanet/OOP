
Pilot orders
------------

**AircraftDirect**
    Change heading from the present time to make a direct on the beacon defined by the Beacon field::

        AircraftDirect Flight=678 Beacon=TOU

    PyRejeu sends a ReportEvent to indicate the order result (OK or ERROR). if necessary PyRejeu ca send a PlnEvent and/or a TrajectoryUpdateEvent

**AircraftTurn**
    Change heading of a flight to make a turn of the number of degrees requested thanks to angle::

        AircraftTurn Flight=77 Angle=15

    PyRejeu sends a ReportEvent to indicate the order result (OK or ERROR). if necessary PyRejeu ca send a PlnEvent and/or a TrajectoryUpdateEvent

**AircraftHeading**
    Change heading from the present time to reach heading given in the field Heading::

        AircraftHeading Flight=77 To=180
        AircraftHeading Flight=77 To=maintain
        AircraftHeading Flight=77 To=90 By=Left
        AircraftHeading Flight=77 To=90 By=Left Rate=2.0

    PyRejeu sends a ReportEvent to indicate the order result (OK or ERROR). if necessary PyRejeu ca send a PlnEvent and/or a TrajectoryUpdateEvent
