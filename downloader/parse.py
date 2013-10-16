from mediameter import parser
from mediacloud.storage import StoryDatabase, MongoStoryDatabase
import time
import ConfigParser

# connect to parse server
parser.connect()

# connect to database of stores to parse
db = "?"

# find stories we still need to parse
stories = "?"

# iterate through stories, adding parsed-out metadata
for story in stories:
	info = parser.parse(story['??'])
	story['parsedInfo'] = info
	db.save_story(story)

# close connection to parse server
parser.close()
