import os
import psycopg2

_dbname = os.environ.get('DB_NAME')
_user = os.environ.get('POSTGRES_USER')
_password = os.environ.get('POSTGRES_PASSWORD')
_host = os.environ.get('POSTGRES_HOST')
_port = os.environ.get('POSTGRES_PORT')

def combined_average(old_rating, old_count, new_rating, new_count):
    ''' This function will combine and old rating/count with an update while
        maintaining an accurate running average '''
    # Make sure no sneaky strings have snuck in...
    old_rating = float(old_rating)
    old_count = int(old_count)
    new_rating = float(new_rating)
    new_count = int(new_count)
    # Calculate a total count and sum
    combined_count = old_count + new_count
    total_ratings = (old_rating * old_count) + (new_rating * new_count)
    # Avoid divide by zero issues
    if combined_count == 0:
        return (0.0, 0)
    # And divide for the new average.
    combined_rating = total_ratings / float(combined_count)
    return (combined_rating, combined_count)
    
def add_records(records):
    ''' Add a or update a record to the database '''
    try:
        # Connect to the database
        conn = psycopg2.connect(dbname=_dbname, user=_user,
            password=_password, host=_host, port=_port)
        cur = conn.cursor()
        
        # Probably don't need to double lock, but if it works don't touch it!
        cur.execute("LOCK TABLE authors in EXCLUSIVE MODE;")
        # Loading everything into memory is a terrible way to scale long-term but the DB really is the bottleneck.
        # Ideally we only want to pull the authors we need to update but I'm not familiar enough with 
        # PostGRES to do it cleanly and quickly. Would definitely consult with someone else but this will
        # get us through the assignment :/
        cur.execute(
            "SELECT id, author, average_rating, rating_count FROM authors FOR UPDATE;")
        
        rows = [{'id':r[0], 'author':r[1], 'average_rating':r[2], 'rating_count':r[3]} for r in cur.fetchall()]

        db_map = {}
        for row in rows:
            db_map[row['author']] = row
            
        for record in records:
            # Handle the insert case
            if record['author'] not in db_map:
                cur.execute(
                    "INSERT INTO authors (author, average_rating, rating_count) VALUES (%s, %s, %s);",
                    (record['author'], record['average_rating'], record['rating_count']))
                
            # Handle the update case
            else:
                row = db_map[record['author']]
            
                # Update the new average based on the combination of the old and new data
                old_rating = float(row['average_rating'])
                old_count = int(row['rating_count'])
                new_rating = record['average_rating']
                new_count = record['rating_count']
                
                combined_score, combined_count = combined_average(old_rating, old_count, new_rating, new_count)
                # Update the record
                cur.execute(
                    f"UPDATE authors SET average_rating=%s, rating_count=%s WHERE id=%s;",
                    (combined_score, combined_count, row['id']))
        conn.commit()
    # Close connections
    finally:            
        if conn:
            cur.close()
            conn.close()
    
