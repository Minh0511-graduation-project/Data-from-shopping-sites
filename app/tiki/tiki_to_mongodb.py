import pymongo
import json


def tiki_to_mongo(db_url):
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    collection = db['suggestion products']

    with open('app/tiki/tiki_products.json') as f:
        data = json.load(f)

    for item in data:
        collection.update_one(
            {"name": item["name"]},
            {"$set": item},
            upsert=True
        )
    print("Push data to MongoDB successfully!")
