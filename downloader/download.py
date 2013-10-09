from mediacloud.api import MediaCloud
from mediacloud.storage import StoryDatabase, MongoStoryDatabase
import time
import ConfigParser

start_time = time.time()

config = ConfigParser.ConfigParser()
config.read('downloader.config')
username = config.get('mediacloud','username')
password = config.get('mediacloud','password')
start_date = config.get('media','start_date')
end_date = config.get('media','end_date')
media_ids = config.get('media','media_ids').split(',')
db_name = config.get('mongo','db_name')
mc = MediaCloud(username, password)

subset_ids = list()

for media_id in media_ids:
	subset_id = mc.createStorySubset(start_date,end_date,media_id)
	subset_ids.append(subset_id)
	print "Created story subset " + subset_id
	
while mc.isStorySubsetReady(subset_ids[-1]) is not True:
	print "Stories aren't ready...Waiting 30 seconds..."
	time.sleep(30)

db = MongoStoryDatabase(db_name)

print "Stories are ready to save to mongodb"

for subset_id in subset_ids:
	more_stories = True
	while more_stories:
	  stories = mc.allProcessedInSubset(subset_id,1)
	  if len(stories)==0:
	    more_stories = False
	  for story in stories:
	    worked = db.addStory(story)

print "Stories are saved to the DB. Tally Ho!"
print "Execution time: " + time.time() - start_time, " seconds"