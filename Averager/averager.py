import pika
import json
import sys, traceback
from time import sleep
from DataModel.commands import add_records, combined_average
import asyncio

def process_data(records):
    ''' Takes an interable of records dicts with an 'author', 'average_rating', and 'rating_count' and returns a list which can be sent to the data model '''
    # We're going to create a dictionary of author names mapped to (total_rating, total_rating_count)
    author_dict = {}
    
    for row in records:
        # We have may have multiple authors separated by commas
        author_field = row['author']
        names = [name.strip() for name in author_field.split(',')]
        # Accumulate results into the dict
        for name in names:
            old_entry = author_dict.get(name, (0.0,0))
            rating, count = combined_average(float(old_entry[0]), int(old_entry[1]), float(row['average_rating']), int(row['rating_count']))
            author_dict[name] = (rating, count)
    
    # Now that we have the full dict we can create a list of the averages
    results = [{
        'author': author,
        'average_rating': author_dict[author][0],
        'rating_count': author_dict[author][1]}
        for author in author_dict]
    
    return results
    
# In theroy this should stop the channel 
async def average_task(batch):
    records = process_data(batch)
    # Send the records to the data model
    add_records(records)
    
def start_listening():
    ''' Gets the next batch of records from the messaging queue '''
    # Setup rabbitmq connection
    # NOTE: This will crash the container if rabbitmq isn't up and Docker has removed the 'depends_on' option
    # We could use our own exception handling loop but Docker handles it fine by restarting the container
    # It would be nice to to start every run with a stacktrace though and enough restarts can affect stdout...
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='average_rating_cmd')

    # Message handler processess and uploads new records
    def on_message(ch, method, properties, body):
        batch = json.loads(body)
        asyncio.run(average_task(batch))

    # Start listener
    print('CONSUME IT ALL')
    channel.basic_consume(
        queue='average_rating_cmd', on_message_callback=on_message, auto_ack=True)
    try:
        channel.start_consuming()
    # I feel like there should be a close on failure condition (or context), 
    # but I've never used rabbitmq...
    finally:
        if connection:
            connection.close()


if __name__ == '__main__': 
    print('START LISTENTING')
    start_listening()

        
