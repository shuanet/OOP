.. _communication-section:

Ivy / ZMQ / AMQP
================

As explained in the introduction, PyRejeu handles three ways to exchange messages with clients:
 * Ivy, as the legacy rejeu application
 * ZeroMQ framework
 * Advanced Message Queuing Protocol

Ivy Bus
--------

When PyRejeu is launch on the Ivy bus, it's acted exactly like the legacy rejeu application. Then, 3 kinds of communication paradigm are used between PyRejeu and a client:
 * *Event dispatching*: PyRejeu sends events to clients, such as the ClockEvent::

      ClockEvent Time=11:22:33

 * *Commands without answer*: in this paradigm, client sends a command to PyRejeu but it does not wait an answer, such as the command::

      ClockStart

 * *Commands with answer*: in this paradigm, client sends a request and expects a response from PyRejeu. In this case, the argument *MsgName* is added to identify the answer::

      GetPosition MsgName=MyClient Flight=45 Time=13:06:35

   Then Pyrejeu answers using the identifier sent by the client::

      Position pos45 Flight=45 CallSign=LB114JQ Ssr=0452 Sector=SL Layers=F,I X=87.00 Y=-128.88 Vx=-197 Vy=265 Afl=195 Rate=2098 Heading=323 GroundSpeed=330 Tendency=1 Time=13:06:38


ZeroMQ
------

PyRejeu also supports the use of ZeroMQ framework to exchange messages with client. In this case, two communication paradigms are used:
 * the Publish/Subscribe paradigm for the diffusion of events. The format of events is exactly the same than for Ivy.
 * the RPC paradigm to send command or get informations from PyRejeu.

.. note::

    For the request/response communication, the **JSON RPC format** is used. For example, *GetPosition* command is formatted as follow::

        {'id': 1, 'method': 'GetPosition', 'params': {'Flight': 101, 'Time': '12:00:00'}}

    Then, PyRejeu answers using the following format::

        {'id': 1, 'result': {'Flight': 101, 'CallSign': 'LB114JQ'...}}


.. note::

    An other important difference with Ivy use is that PyRejeu answers to each command, such as *ClockStart*.
    For simple command, PyRejeu simply sends an acknowledgement::

        {'id': 2, 'result': True}


**Launch PyRejeu with zmq**
    To use PyRejeu with zmq, you need to specify a bus id following the format zmq://*\:port1\:port2
     * The first port number is for the rpc exchanges. PyRejeu binds a REP socket to this port.
     * The second one is for the diffusion of events. Pyrejeu binds en PUB socket to this port.

**Write zmq client for Pyrejeu**
    A client which wants to use zmq needs to setup two sockets.
     * The first one to send commands (type REQ)
     * The second one to receive events (type SUB).

    You can find an example written in python below.

.. code-block:: python

    import zmq
    import json

    host = 'localhost'
    rpc_port = 6000
    evt_port = 6001

    # send command
    rpc_socket = zmq.Context().socket(zmq.REQ)
    rpc_socket.connect("tcp://{0}:{1}".format(host, rpc_port))
    request = json.dumps({'id': 1, 'method': 'GetPosition',
                          'params': {'Flight': 101, 'Time': '12:00:00'}})
    rpc_socket.send(request.encode())
    # wait for a response
    response = json.loads(rpc_socket.recv().decode())
    print(response['result'])

    # record events
    evt_socket = zmq.Context().socket(zmq.SUB)
    evt_socket.connect("tcp://%s:%s" % (host, evt_port))
    # subscribe to all events
    evt_socket.setsockopt(zmq.SUBSCRIBE, b'')

    poller = zmq.Poller()
    poller.register(evt_socket, zmq.POLLIN)
    while True:
        evts = dict(poller.poll(timeout=0.1))
        if evt_socket in evts:
            print(evt_socket.decode())

AMQP
------

PyRejeu also supports AMQP. So, it can connect to server like *rabbitmq* to communicate with clients.

The principle is identical to ZMQ.
 * JSON-RPC format is used for RPC communications.
 * a queue (named **pyrejeu_rpc_queue**) is dedicated to RPC commands.
 * an exchange (named **pyrejeu_event_exchange**) is dedicated for diffusion of events.

**Launch PyRejeu with amqp**
    To use PyRejeu with amqp, you need to specify a bus id following the format amqp://<host>:<port>. Most of the time, you will use::

        amq://localhost:5672

**Write amqp client for Pyrejeu**

    The code below is an example of client using amqp and written in python.

.. code-block:: python

    import pika
    import uuid
    import json

    url = 'amqp://localhost:5672'
    connection = pika.BlockingConnection(pika.URLParameters(url))
    channel = connection.channel()

    # rpc commands
    response = None
    cor_id = None
    def on_response(ch, method, props, body):
        global response, corr_id
        if corr_id == props.correlation_id:
            response = json.loads(body.decode())

    result = channel.queue_declare(exclusive=True)
    callback_queue = result.method.queue
    channel.basic_consume(on_response, no_ack=True,
                          queue=callback_queue)

    corr_id = str(uuid.uuid4())
    request = json.dumps({'id': 1, 'method': 'GetPosition',
                          'params': {'Flight': 101, 'Time': '12:00:00'}})
    channel.basic_publish(exchange='',
                          routing_key='pyrejeu_rpc_queue',
                          properties=pika.BasicProperties(
                               reply_to=callback_queue,
                               correlation_id=corr_id,
                          ),
                          body=request.encode())
    while response is None:
        connection.process_data_events(time_limit=0.1)
    print(response)

    # record events
    def on_event(ch, method, props, body):
        print(body.decode())

    channel.exchange_declare(exchange='pyrejeu_event_exchange', type='topic')
    result = channel.queue_declare(exclusive=True)
    evt_queue = result.method.queue
    channel.queue_bind(exchange='pyrejeu_event_exchange',
                       queue=evt_queue,
                       routing_key="evt.*")
    channel.basic_consume(on_event, no_ack=True, queue=evt_queue)
    channel.start_consuming()
