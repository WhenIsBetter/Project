import random
import string

import mongomock

from database import Database
from scheduler.TimeRange import TimeRange
from spm_bot.Event import Event


# A fake database used for automated tests.
class MockDatabase(Database.Database):

    # Need to override to mock client instead of our actual databases
    def __init__(self):

        # The client in charge of the cluster of databases
        self._database_cluster_client = mongomock.MongoClient()
        # The database specifically tailored for our discord bot
        self._discord_bot_database = self._database_cluster_client.db
        # In this database that we just accessed, we can now use 'collections' which are like folders
        # These 'folders' contain mongo 'documents' which are basically json files that easily translate to
        # Python dictionaries
        self._event_collection = self._discord_bot_database.collection

    # Since this library isn't async but our bot relies on an async database, we have to override these methods sigh

    async def generate_unique_id(self):

        random_id = ''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(Database.UNIQUE_ID_LENGTH)])

        # Is there already a document with this ID? If so, try again
        if self._event_collection.find_one({'_id': random_id}):
            return await self.generate_unique_id()

        # Sweet, it's a unique ID
        return random_id

    # Creates a new event to store in the database for edit/retrieval later, returns the document once created
    async def create_event(self, event: Event) -> dict:

        # In order to store time ranges correctly, we neeed to mutate it into something mongo can understand
        new_attendees = {}
        for attendee, list_of_bad_times in event.attendees.items():
            # A list of tuples
            tuple_ranges = []
            for bad_time in list_of_bad_times:
                tuple_ranges.append((bad_time.start, bad_time.end))

            new_attendees[str(attendee)] = tuple_ranges

        # Mongo documents are literally just python dictionaries
        document = {
            '_id': await self.generate_unique_id(),
            'start': event.start,
            'end': event.end,
            'guild': event.guild,
            'organizer': event.eventOrganizer,
            'attendees': new_attendees
        }

        # Insert the document to the database and return it if we need further processing where this was called
        self._event_collection.insert_one(document)
        return document

    # Retrieves an event stored in the database given an event ID, if event with ID doesn't exist, returns None
    async def get_event(self, id) -> Event:

        # Find the document with the ID
        document = self._event_collection.find_one({'_id': id})
        # Possible that document doesn't exist
        if not document:
            return None

        # Construct an event object to return
        event = Event(document['start'], document['end'], document['organizer'], document['guild'])

        # We need to construct the attendees to fit the Event class format
        for attendee, list_of_bad_times in document['attendees']:

            timerange_list = []

            for bad_time in list_of_bad_times:
                timerange_list.append(TimeRange(bad_time[0], bad_time[1]))

            event.update_attendee_conflicting_times(int(attendee), timerange_list)
        return event

    # Pass in event id and a dictionary that contains keys to updated values to overwrite, for example, passing in a
    # dict that only contains key 'start' which maps to a datetime object, we will update the event in the database
    # by only replacing the new 'start' value while retaining all the old ones. Returns the new event object
    async def update_event(self, id, updated_kvps: dict) -> Event:
        self._event_collection.update_one({'_id': id}, {'$set': updated_kvps})
        return await self.get_event(id)

    # Deletes an event from the database given an event ID, returns the Event deleted if found
    async def delete_event(self, id):

        event: Event = await self.get_event(id)
        if not event:
            return None

        self._event_collection.delete_one({'_id': id})
        return event