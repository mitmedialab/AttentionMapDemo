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
		#self.cleanupConfig()
		print "Execution time: " + str(time.time() - start_time), " seconds"

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
		print "Starting with page " + str(page)
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
				worked = self.db.addStory(story,save_extracted_text=True)
				
			print "Saved stories on page " + str(page)
			page=int(page)
			page+=1
			pages_written+=1
			self.config.set("state", "page_num", page)
			self.writeConfig()
		if more_stories is not True:
			self.cleanupConfig()


	def writeConfig(self):
		cfgfile = open("downloader.config",'w')
		self.config.write(cfgfile)
		cfgfile.close()

	def cleanupConfig(self,state=''):
		self.config.set('state', 'state', state)
		self.config.set('state', 'media_id', '')
		self.config.set('state', 'subset_id', '')
		self.config.set('state', 'page_num', '')
		self.writeConfig()

	def run(self): 
		state = self.config.get('state','state')
		media_id = self.config.get('state','media_id')
		subset_id = self.config.get('state','subset_id')
		page_num = self.config.get('state','page_num')
		print "------------------------------------"
		print "Current state information: "
		print "State: " + state
		print "Media id: " + media_id
		print "Subset id: " + subset_id
		print "Page number: "+ page_num
		print "------------------------------------"

		if state == 'finished':
			print "It looks like you already finished this job. Check your DB for the presence of the stories. If you think you are receiving this message in error, remove the 'finished' value from the config file."
		elif (state == "creation" or state == "waiting") and subset_id is not None:
			print "Starting in the waiting state..."
			self.wait(subset_id)
			self.fetch(subset_id)
			self.runAllStates(self.getNewIDList(media_id))
		elif state == "fetching":
			print "Starting in the fetching state..."
			self.fetch(subset_id, page_num)
			self.runAllStates(self.getNewIDList(media_id))
		else:
			print "Starting everything from the beginning..."
			self.runAllStates(self.media_ids)

		self.cleanupConfig('finished')
			
	def runAllStates(self, media_ids):
		for media_id in media_ids:
				subset_id = self.create(media_id)
				self.wait(subset_id)
				self.fetch(subset_id)

	def getNewIDList(self, media_id):
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
