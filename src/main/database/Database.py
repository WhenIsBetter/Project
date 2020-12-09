# Mongo databases are essentially just a way to persistently store python dictionaries when using the python driver.
# Since we are using an asynchronous discord bot, we are going to use the asynchronous mongo driver known as 'motor'
# It functions exactly the same as mongo, meaning you can still use the documentation provided by mongo to interact with
# the database but any functions that are called that interact with the database need to be async/awaited.
import random
import string

from motor import motor_asyncio

from spm_bot.Event import Event

# TODO: maybe move this to a config later down the road, if someone were to deploy this and have an external db running
#       non-locally it would make deployment way easier
DATABASE_URL = "localhost"
DATABASE_PORT = 27017

UNIQUE_ID_LENGTH = 8  # How long should we make our unique IDs for events?


# We will attach this Database class to our discord bot
class Database:

    def __init__(self):

        # The client in charge of the cluster of databases
        self.__database_cluster_client = motor_asyncio.AsyncIOMotorClient(DATABASE_URL, DATABASE_PORT)
        # The database specifically tailored for our discord bot
        self.__discord_bot_database = self.__database_cluster_client['discord']
        # In this database that we just accessed, we can now use 'collections' which are like folders
        # These 'folders' contain mongo 'documents' which are basically json files that easily translate to
        # Python dictionaries
        self.__event_collection = self.__discord_bot_database['events']
        self.__token_collection = self.__discord_bot_database['tokens']

    async def generate_unique_id(self):

        random_id = ''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(UNIQUE_ID_LENGTH)])

        # Is there already a document with this ID? If so, try again
        if await self.__event_collection.find_one({'_id': random_id}):
            return await self.generate_unique_id()

        # Sweet, it's a unique ID
        return random_id

    # Creates a new event to store in the database for edit/retrieval later, returns the document once created
    async def create_event(self, event: Event) -> dict:

        # Mongo documents are literally just python dictionaries
        document = {
            '_id': await self.generate_unique_id(),
            'start': event.start,
            'end': event.end,
            'organizer': event.eventOrganizer,
            'attendees': event.attendees
        }

        # Insert the document to the database and return it if we need further processing where this was called
        await self.__event_collection.insert_one(document)
        return document

    # Add a discord users calendar api auth code to the database and return it if we need it for further processing or
    # testing
    async def add_calendar_creds(self, discord_user_id, auth_code):
        document = {
            'discord_id': discord_user_id,
            'auth_code': auth_code
        }

        await self.__token_collection.insert_one(document)
        return document

    # Retrieves an event stored in the database given an event ID, if event with ID doesn't exist, returns None
    async def get_event(self, id) -> Event:

        # Find the document with the ID
        document = await self.__event_collection.find_one({'_id': id})
        # Possible that document doesn't exist
        if not document:
            return None

        # Construct an event object to return
        event = Event(document['start'], document['end'])
        event.eventOrganizer = document['organizer']
        event.attendees = document['attendees']
        return event

    # Deletes an event from the database given an event ID, returns the Event deleted if found
    async def delete_event(self, id):

        event: Event = await self.get_event(id)
        if not event:
            return None

        await self.__event_collection.delete_one({'_id': id})
        return event
