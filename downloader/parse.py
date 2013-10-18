from mediameter import parser
from mediameter.db import ParseableStoryDatabase
import time, logging, ConfigParser

log = logging.getLogger('parser')

config = ConfigParser.ConfigParser()
config.read('downloader.config')

# connect to parse server
parser.connect()

# connect to database of stores to parse
db = ParseableStoryDatabase(config.get('mongo','db_name'),config.get('mongo','host'),int(config.get('mongo','port')))

# find stories we still need to parse
stories = db.unparsedArticles()
log.info('Fetched '+str(len(stories))+' that need to be parsed')

# iterate through stories, adding parsed-out metadata
for story in stories:
	info = parser.parse(story['story_text'])
	db.updateStory(story['_id'],{
		'meta': info
	})

# close connection to parse server
parser.close()
