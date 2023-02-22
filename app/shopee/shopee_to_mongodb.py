import pymongo
import json


def shopee_to_mongo(db_url):
    client = pymongo.MongoClient(db_url)
    db = client['Shop-search-system']
    products = db['shopee products']
    search_suggestions = db['shopee search suggestions']

    with open('app/shopee/shopee_search_suggestions.json') as f:
        search_suggestions_data = json.load(f)

    for item in search_suggestions_data:
        search_suggestions.update_one(
            {"keyword": item["keyword"]},
            {"$set": item},
            upsert=True
        )

    with open('app/shopee/shopee_products.json') as f:
        products_data = json.load(f)

    for item in products_data:
        products.update_one(
            {"name": item["name"]},
            {"$set": item},
            upsert=True
        )
    print("Push shopee data to MongoDB successfully!")
