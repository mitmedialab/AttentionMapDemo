from mediacloud.api import MediaCloud
from mediacloud.storage import StoryDatabase, MongoStoryDatabase
import time
import ConfigParser

class Downloader():

	def __init__(self):
		start_time = time.time()
		self.config = ConfigParser.ConfigParser()
		self.config.read('downloader.config')
		self.media_ids = self.config.get('media','media_ids').split(',')
		self.mc = MediaCloud(self.config.get('mediacloud','username'), self.config.get('mediacloud','password'))
		self.db = MongoStoryDatabase(self.config.get('mongo','db_name'))
		self.run()
		print "Execution time: " + time.time() - start_time, " seconds"

	def create(self, media_id):
		print "Creating..."
		self.config.set("state", "media_id", media_id)
		self.config.set("state", "state", "creation")
		self.writeConfig()
		
		subset_id = self.mc.createStorySubset(self.config.get('media','start_date'),self.config.get('media','end_date'),media_id)
		
		self.config.set("state", "subset_id", subset_id)
		self.writeConfig()
		return subset_id

	def wait(self, subset_id):
		print "Waiting..."
		self.config.set("state", "state", "waiting")
		self.writeConfig()
		while self.mc.isStorySubsetReady(subset_id) is not True:
			print "Stories aren't ready...Waiting 30 seconds..."
			time.sleep(30)

	def fetch(self, subset_id, page=1):
		print "Fetching..."
		max_pages = self.config.get("state","max_pages")
		self.config.set("state", "state", "fetching")
		self.writeConfig()
		more_stories = True
		pages_written = 0
		while more_stories and (pages_written <= max_pages or max_pages == 0):
			stories = self.mc.allProcessedInSubset(subset_id,page)
			if len(stories)==0:
				more_stories = False
			for story in stories:
				worked = db.addStory(story,save_extracted_text=True)
			page+=1
			pages_written+=1
			self.config.set("state", "page_num", page)
			self.writeConfig()

	def writeConfig(self):
		cfgfile = open("downloader.config",'w')
		self.config.write(cfgfile)
		cfgfile.close()
	
	def run(self): 
		state = self.config.get('state','state')
		media_id = self.config.get('state','media_id')
		subset_id = self.config.get('state','subset_id')
		page_num = self.config.get('state','page_num')

		if (state is "creation" or state is "waiting") and subset_id is not None:
			self.wait(subset_id)
			self.fetch(subset_id)
			self.runAllStates(newMediaIds(media_id))
		if state is "fetching":
			self.fetch(subset_id, page_num)
			self.runAllStates(newMediaIds(media_id))
		else:
			self.runAllStates(self.media_ids)
			
	def runAllStates(self, media_ids):
		for media_id in media_ids:
				subset_id = self.create(media_id)
				self.wait(subset_id)
				self.fetch(subset_id)

	def newMediaIds(self, media_id):
		newList = self.media_ids[:]
		for i in range(len(newList)):
			if newList[i] != media_id:
				newList.pop(i)
			if newList[i] == media_id:
				newList.pop(i)
				break
		return newList

d = Downloader()

print "Stories are saved to the DB. Tally Ho!"
