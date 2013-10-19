import sys, time, logging, ConfigParser
from mediameter import parser
from mediameter.db import ParseableStoryDatabase

config = ConfigParser.ConfigParser()
config.read('downloader.config')

# connect to parse server
parser.connect()
print "Connected to parser"

# connect to database of stores to parse
db = ParseableStoryDatabase(config.get('mongo','db_name'),config.get('mongo','host'),int(config.get('mongo','port')))

# find stories we still need to parse
stories = db.unparsedArticles()
print 'Fetched '+str(len(stories))+' that need to be parsed'

# iterate through stories, adding parsed-out metadata
for story in stories:
	info = parser.parse( ' '.join(story['sentences'].values()) )
	db.updateStory(story['_id'],{
		'meta': info
	})

# close connection to parse server
parser.close()
print "Done"