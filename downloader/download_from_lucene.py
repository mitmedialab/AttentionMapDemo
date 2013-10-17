from mediameter.lucene import Lucene
from mediacloud.api import MediaCloud
from mediacloud.storage import StoryDatabase, MongoStoryDatabase
import logging
import time
import ConfigParser

class LuceneDownloader():

	def __init__(self):
		start_time = time.time()
		self.log = logging.getLogger('mediacloud')
		self.config = ConfigParser.ConfigParser()
		self.config.read('downloader.config')
		self.media_ids = self.config.get('media','media_ids').split(',')
		self.mc = MediaCloud(self.config.get('mediacloud','username'), self.config.get('mediacloud','password'))
		self.db = MongoStoryDatabase(self.config.get('mongo','db_name'))
		self.run()
		self.log.info("Execution time: " + str(time.time() - start_time), " seconds")

	def create(self, media_id):
		self.log.info("Creating...")
		self.config.set("state", "media_id", media_id)
		self.config.set("state", "state", "creation")
		self.writeConfig()
		
		lucene = Lucene(self.config.get('media','start_date'),self.config.get('media','end_date'),media_id)
		result_count = lucene.get_sentence_count()
		
		self.config.set("state", "result_count", str(result_count))
		self.writeConfig()
		return "fetching"

	def fetch(self, page=0):
		self.log.info("Fetching...")
		media_id = self.config.get("state", "media_id")
		max_pages = int(self.config.get("state","max_pages"))
		result_count = int(self.config.get("state", "result_count"))
		self.config.set("state", "state", "fetching")
		self.writeConfig()
		more_sentences = True
		pages_written = 0
		self.log.info("Starting with page " + str(page) + " (up to "+str(max_pages)+" pages)")
		lucene = Lucene(self.config.get('media','start_date'),self.config.get('media','end_date'),media_id)
		while more_sentences and ( (pages_written <= max_pages) or (max_pages == 0) ) and ((page-1)*lucene.SENTENCES_PER_PAGE <= result_count):
			sentences = lucene.get_sentences( page )
			if len(sentences)==0:
				more_sentences = False
			for sentence in sentences:
				worked = True
				# create story if needed
				if not self.db.storyExists(sentence['stories_id']):
					self.db._saveStory({ # bypass addStory because we don't have the fields
						'_id': int(sentence['stories_id']),
						'media_id': sentence['media_id'],
						'story_text': ''
					})
				# add sentence to existing story (http://docs.mongodb.org/manual/reference/method/db.collection.update/#db.collection.update)
				existing_text = self.db.getStory(sentence['stories_id'])['story_text']
				self.db._db.stories.update(
					{'_id':int(sentence['stories_id'])},
					{'$set':{
						'story_text': existing_text+" "+sentence['sentence']
					}}
				)
			self.log.info("Saved sentences on page " + str(page))
			page=int(page)
			page+=1
			pages_written+=1
			self.config.set("state", "page_num", page)
			self.writeConfig()
		if page*lucene.SENTENCES_PER_PAGE >= result_count:
			return 'finished'
		if more_sentences is True:
			return "exit"
		else:
			self.cleanupConfig()
			return "finished"

	def writeConfig(self):
		cfgfile = open("downloader.config",'w')
		self.config.write(cfgfile)
		cfgfile.close()

	def cleanupConfig(self,state=''):
		self.config.set('state', 'state', state)
		self.config.set('state', 'media_id', '')
		self.config.set('state', 'page_num', '')
		self.writeConfig()

	def run(self): 
		state = self.config.get('state','state')
		media_id = self.config.get('state','media_id')
		page_num = self.config.get('state','page_num')
		if page_num is None or len(page_num)==0:
			page_num = 0
		else:
			page_num = int(page_num)
		self.log.info("------------------------------------")
		self.log.info("Current state information: ")
		self.log.info("State: " + state)
		self.log.info("Media id: " + media_id)
		self.log.info("Page number: "+ str(page_num))
		self.log.info("------------------------------------")

		while state is not "exit":
			if state == 'finished':
				self.cleanupConfig('finished')
				print "It looks like you already finished this job. Check your DB for the presence of the stories. If you think you are receiving this message in error, remove the 'finished' value from the config file."
				next_state = 'exit'
			elif state == 'fetching':
				self.log.info("In the fetching state...")
				next_state = self.fetch(page_num)
			elif (state == None) or (state == "creation") or (len(state)==0):
				self.log.info("In the creation state...")
				next_state = self.create(self.media_ids[0])
			print "from "+state+" to "+next_state
			state = next_state

d = LuceneDownloader()

print "Stories are saved to the DB. Tally Ho!"
