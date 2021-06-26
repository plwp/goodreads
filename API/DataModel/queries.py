import os
import psycopg2

_dbname = os.environ.get('DB_NAME')
_user = os.environ.get('POSTGRES_USER')
_password = os.environ.get('POSTGRES_PASSWORD')
_host = os.environ.get('POSTGRES_HOST')
_port = os.environ.get('POSTGRES_PORT')


def get_top(n=50):
    ''' Returns the top n records from the data model sorted by average rating '''
    try:
        # Connect to the database
        conn = psycopg2.connect(dbname=_dbname, user=_user,
            password=_password, host=_host, port=_port)
        cur = conn.cursor()
        cur.execute(
            f"SELECT author, average_rating, rating_count FROM authors ORDER BY average_rating DESC, rating_count DESC LIMIT %s;",[n])
        
        # We'd normally use a class rather than a dict but this way lets us split the module cleanly
        # which means we can avoid scripts which have to inject it into the docker images 
        result = [{'author':r[0], 'average_rating':r[1], 'rating_count':r[2]} for r in cur.fetchall()]
        return result

    # Close connections
    finally:            
        if conn:
            cur.close()
            conn.close()
