import math
from mediacloud.storage import MongoStoryDatabase
from bson.code import Code

class ParseableStoryDatabase(MongoStoryDatabase):
    '''
    '''

    def saveNewStory(self, story):
        self._saveStory(story)

    def updateStory(self, story_id, props):
        self._db.stories.update(
            { '_id':int(story_id) },
            { '$set': props }
        )

    def unparsedArticles(self, count=10):
        results = self._db.stories.find({"meta":{'$exists': False}}).limit(count)
        stories = []
        for item in results:
            stories.append(item)
        return stories
