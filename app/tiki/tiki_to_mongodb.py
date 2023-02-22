import pymongo
import json


def tiki_to_mongo(db_url):
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    products = db['tiki products']
    search_suggestions = db['tiki search suggestions']

    with open('app/tiki/tiki_search_suggestions.json') as f:
        search_suggestions_data = json.load(f)

    for item in search_suggestions_data:
        search_suggestions.update_one(
            {"keyword": item["keyword"]},
            {"$set": item},
            upsert=True
        )

    with open('app/tiki/tiki_products.json') as f:
        products_data = json.load(f)

    for item in products_data:
        products.update_one(
            {"name": item["name"]},
            {"$set": item},
            upsert=True
        )
    print("Push tiki data to MongoDB successfully!")
