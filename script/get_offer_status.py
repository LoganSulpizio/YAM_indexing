if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import sqlite3
from typing import List, Dict, Any

def get_all_events_from_offer_id(cursor: sqlite3.Cursor, offer_id: int) -> List[Dict[str, Any]]:
    result = []

    # Query to get the offer from the offers table
    cursor.execute("SELECT * FROM offers WHERE offer_id = ?", (offer_id,))
    offer = cursor.fetchone()

    # If the offer exists, add it to the result list
    if offer:
        result.append(dict(zip([column[0] for column in cursor.description], offer)))

        # Query to get all events related to this offer from offer_events table
        cursor.execute("SELECT * FROM offer_events WHERE offer_id = ? ORDER BY event_timestamp ASC", (offer_id,))
        events = cursor.fetchall()

        # Add each event to the result list
        for event in events:
            result.append(dict(zip([column[0] for column in cursor.description], event)))

    return result

def get_offer_status(cursor: sqlite3.Cursor, offer_id: int) -> str:
    
    events = get_all_events_from_offer_id(cursor, offer_id)

    # Iterate over the events list
    last_offer_updated_index = None
    
    for i, event in enumerate(events):

        if event.get('event_type', None) == 'OfferUpdated':
            # Keep track of the index of the last 'OfferUpdated' event
            last_offer_updated_index = i
    
    # If an 'OfferUpdated' event was found, slice the list from that event onwards
    if last_offer_updated_index is not None:
        events = events[last_offer_updated_index:]
    
    if len(events) > 0:
        amount = int(events[0].get('initial_amount', events[0].get('amount', None)))
        for event in events[1:]:
            amount -= int(event['amount_bought'])
    else:
        return None

    if amount is None:
        return None
    elif amount == 0:
        return 'SoldOut'
    elif amount > 0: 
        return 'InProgress'
    else:
        return None




if __name__ == "__main__":
    from pprint import pprint
    # Connect to the SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect('YAM.db')

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    status = get_offer_status(cursor, 56882)

    print(status)