from flask import Blueprint, Flask, jsonify, request, Response, redirect
from DataModel.queries import get_top
import json
import pika
import asyncio

app = Flask(__name__)
api = Blueprint('api', __name__)

# Our authentication stubs
class AuthenticationFailedException(Exception):
    pass
class AuthenticationMissingException(Exception):
    www_authenticate = ''
def authenticate(credentials):
    ''' Stub for authentication. '''
    # Let's do the classic developer trick of ignoring authentication and forgetting to implement it later...
    pass

# We could do some cheap formatting checks e.g. a random record, length limit and report the user if they messed up.
# Or we could send it off to an imaginary service for clever standardization to fix things like name
# formatting and data poisoning.
async def ingress(data):
    ''' Stub of the ingress service. '''    
    # But as it turns out we'll just pump the data into rabbitmq sight unseen...
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    try:
        channel = connection.channel()
        channel.queue_declare(queue='average_rating_cmd')
        body = json.dumps(data)
        channel.basic_publish(exchange='', routing_key='average_rating_cmd', body=body)
    finally:
        if connection:
            connection.close()

### Routes
@api.route('/update', methods=['POST'])
def update():
    try:
        authenticate(request.headers.get('Authorization'))
        json_data = request.get_json()
        if json_data:
            asyncio.run(ingress(json_data))
            # We could provide better feedback but this way is a) quicker and b) harder to break.
            return "forwarded to ingress service", 200
        # The bare minimum of sanity checking
        return "posted data must be json list of records", 400

    # Here's where we might handle authentication problems. There are probably better 
    # patterns in a framework but at least we're trying.
    except AuthenticationFailedException:
        return "authentication failed", 403
    except AuthenticationMissingException as e:
        resp = Response("authentication required")
        resp.headers['www-Authenticate'] = e.www_authenticate
        return resp

@api.route('/top-authors/<number>', methods=['GET'])
def top_authors_by_avg_rating(number):
    ''' Returns a list of the top authors by average rating, thus meeting the requirements.'''
    result = get_top(int(number))
    return json.dumps(result), 200    

@api.route('/alive', methods=['GET'])
def alive():
    ''' Just used for configuration troubleshooting. Will respond "I'm alive" to GET requests.'''
    return "I'm alive", 200     
        
app.register_blueprint(api, url_prefix="/api")

if __name__ == '__main__':
    app.run()
