from pymongo import MongoClient

class MongoDB:
    def __init__(self):
        super().__init__()
        client = MongoClient('INSERT_YOUR_OWN_IP', 27017, username='INSERT_YOUR_OWN_USERNAME', password='INSERT_YOUR_OWN_PASSWORD')
        self.ttds = client.ttds
        self.sentences = self.ttds.sentences
        self.inverted_index = self.ttds.inverted_index
        self.movies = self.ttds.movies
        self.sentences.create_index('_id')
        self.inverted_index.create_index('_id')
        self.movies.create_index('_id')
        self.inverted_index_gridfs = gridfs.GridFS(self.ttds)
