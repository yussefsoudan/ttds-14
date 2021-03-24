from pymongo import MongoClient

DB_PASS='thenittygrittyofELnitty'
DB_USER='readerTTDS'
DB_NAME='TTDS' 
DB_HOST='188.166.173.191'
PORT = '27017'
client = MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}') 
db = client[DB_NAME]
print(db["invertedIndex"].count_documents({}))