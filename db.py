import pymongo

myclient = pymongo.MongoClient("mongodb://mongo:27017/")

mydb = myclient["mydatabase"]

mycol = mydb["imagedb"]
