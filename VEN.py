import asyncio
from datetime import timedelta
from openleadr import OpenADRClient, enable_default_logging
from openleadr import utils
enable_default_logging()

async def collect_report_value():
    # This callback is called when you need to collect a value for your Report
    print("Collect report value called")
    return 1.23

async def handle_event(event):
    #print('Handle event called')
    # This callback receives an Event dict.
    # You should include code here that sends control signals to your resources.
    print("******** EVENT RECEIVED *********")
    print(event)
    return 'optIn'

async def event_response_callback():
    return 1

# Create the client object
client = OpenADRClient(ven_name='ven123', vtn_url='http://129.73.13.185:8888/OpenADR2/Simple/2.0b',ven_id='ven_id_123')
#print('OpenADR Client done')
#print(utils.generate_id())

# Add the report capability to the client
client.add_report(callback=collect_report_value,
                  resource_id='device001',
                  measurement='voltage',
                  sampling_rate=timedelta(seconds=1),
                  report_duration=timedelta(seconds=30))

#client.add_report(callback=event_response_callback,resource_id='device001',measurement='voltage',sampling_rate=timedelta(seconds=2))
#print('Add Report Done')

# Add event handling capability to the client
client.add_handler('on_event', handle_event)
#print('event added')

# Run the client in the Python AsyncIO Event Loop
loop = asyncio.get_event_loop()
loop.create_task(client.run())
loop.run_forever()
#print('Loop Running')

loop.close()
