
Misc Requests
-------------

**FileWrite**
    Request to PyRejeu to save the data as it knows them at the time of the request::

        FileWrite Type=dump Name=echantillon.txt

.. note ::

    Currently, only *dump* type is supported by PyRejeu.

**CancelLastOrder**
    Ask PyRejeu to cancel the last modification received for the flight identified by the Flight parameter::

        CancelLastOrder Flight=6532

**Discard**
    Ask PyRejeu to ignore the flight identified by the Flight parameter::

        Discard Flight=987

**DiscardAll**
    Ask PyRejeu to ignore all the flights::

        DiscardAll

**Enable**
    Ask PyRejeu to cancel the discard order for the flight identified by the Flight parameter::

        Enable Flight=987