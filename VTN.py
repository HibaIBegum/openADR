import asyncio
from datetime import datetime, timezone, timedelta
from openleadr.objects import Event, EventDescriptor, EventSignal, Target, Interval
from openleadr import OpenADRServer, enable_default_logging
from functools import partial

enable_default_logging()

async def on_create_party_registration(registration_info):
    """
    Inspect the registration info and return a ven_id and registration_id.
    """
    #print(registration_info)
    if len(registration_info['ven_name']) > 0:
        ven_id =  registration_info['ven_id']
        registration_id = registration_info['ven_name']
        return ven_id, registration_id
    else:
        return False

async def on_register_report(ven_id, resource_id, measurement, unit, scale,
                             min_sampling_interval, max_sampling_interval):
    """
    Inspect a report offering from the VEN and return a callback and sampling interval for receiving the reports.
    """
    callback = partial(on_update_report, ven_id=ven_id, resource_id=resource_id, measurement=measurement)
    sampling_interval = min_sampling_interval
    return callback, sampling_interval

async def on_update_report(data, ven_id, resource_id, measurement):
    """
    Callback that receives report data from the VEN and handles it.
    """
    for time, value in data:
        print('Call from update report function')
        print(data)
        print(f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}")

async def event_response_callback(ven_id, event_id, opt_status):
    """
    Callback that receives the response from a VEN to an Event.
    """
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!date')
    print('Call from event response function')
    print(f"VEN {ven_id} responded to Event {event_id} with: {opt_status}")

async def event_callback(ven_id, event_id, opt_type):
    print("******event callback ********")
    print(f"VEN {ven_id} responded {opt_status} to event {event_id}")

# Create the server object
server = OpenADRServer(vtn_id='myvtn',http_host='129.73.13.185',http_port='8888')

# Add the handler for client (VEN) registrations
server.add_handler('on_create_party_registration', on_create_party_registration)

# Add the handler for report registrations from the VEN
server.add_handler('on_register_report', on_register_report)

# Add a prepared event for a VEN that will be picked up when it polls for new messages.
'''server.add_event(ven_id='ven_id_123',
                 signal_name='simple',
                 signal_type='level',
                 intervals=[{'dtstart': datetime.now(),
                             'duration': timedelta(seconds=8),
                             'signal_payload': 1}],
                 callback=event_response_callback)
#		response_required = 'never')
'''
now = datetime.now()
event = Event(event_descriptor=EventDescriptor(event_id='event001',
                                               modification_number=0,
                                               event_status='far',
                                               market_context='http://marketcontext01'),
              event_signals=[EventSignal(signal_id='signal001',
                                         signal_type='level',
                                         signal_name='simple',
                                         intervals=[Interval(dtstart=now,
                                                             duration=timedelta(minutes=10),
                                                             signal_payload=1)]),
                             EventSignal(signal_id='signal002',
                                         signal_type='price',
                                         signal_name='ELECTRICITY_PRICE',
                                         intervals=[Interval(dtstart=now,
                                                             duration=timedelta(minutes=10),
                                                             signal_payload=1)])],
              targets=[Target(ven_id='ven123')])

server.add_raw_event(ven_id='ven123', event=event, callback=event_callback)

# Run the server on the asyncio event loop
loop = asyncio.get_event_loop()
loop.create_task(server.run())
loop.run_forever()

loop.close()
