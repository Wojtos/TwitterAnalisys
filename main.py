from Action.ArgumentActionParser import ArgumentActionParser
from Database.MongoTwitterDB import MongoTwitterDB
from dotenv import load_dotenv

from Database.TwitterDB import TwitterDB

if __name__ == '__main__':

    load_dotenv()

    mongo_db = MongoTwitterDB()
    TwitterDB.instance = mongo_db

    action_parser = ArgumentActionParser()
    action = action_parser.parse()
    print(action.execute())
    print(mongo_db.find_twitts_count())
