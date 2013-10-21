import sys, time, logging, ConfigParser, json
from mediameter.lucene import Lucene
from mediameter import parser
from mediameter.db import ParseableStoryDatabase
from iso3166 import countries
import mediacloud.api
import operator
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import string, math

DO_IF_IDF = False

config = ConfigParser.ConfigParser()
config.read('downloader.config')

# connect to database
db = ParseableStoryDatabase(config.get('mongo','db_name'),config.get('mongo','host'),int(config.get('mongo','port')))

output = []	# the thing to jsonify at the end

# get list of all media sources
media_counts = db.storyCountByMediaSource()
for media_id_str, story_count in media_counts.iteritems():
	print "Working on media "+media_id_str
	info = {
		'mediaId': int(media_id_str),
		#'articleCount': story_count,
		'mediaName': mediacloud.api.mediaSource(media_id_str)['name']
	}

	# setup tfidf computation
	if DO_IF_IDF:
		print "  Setting up media text collection"
		text_by_country = {}
		for country_code, count in db.storyCountByCountry(media_id_str).iteritems():
			country_stories = db.mediaStories(media_id_str, country_code)
			country_stories_text = ' '.join( [ ' '.join( doc['sentences'].values() )  for doc in country_stories] )
			country_text = nltk.Text([word.encode('utf-8') for sent in sent_tokenize(country_stories_text.lower()) for word in word_tokenize(sent)])
			text_by_country[country_code] = country_text
		text_collection = nltk.TextCollection(text_by_country.values())
		print "    done"

	# now create results we care about
	print "  Computing aggregate info"
	count_by_country = []
	parsed_article_count = 0
	for country_code, count in db.storyCountByCountry(media_id_str).iteritems():
		# setup country-specific info
		country_alpha3 = None
		country_stopwords = []
		try:
			country_iso3166 = countries.get(country_code)
			country_alpha3 = country_iso3166.alpha3
			country_stopwords.append( country_iso3166.name.lower() )
		except KeyError:
			# not sure how to handle things that aren't fully approved, like XK for Kosovo :-(
			print 'Unknown country code '+country_code
			country_alpha3 = None			
		
		if DO_IF_IDF:
			# compute document term frequency for stories about this country from this media source
			tfidf = {}
			print "    Calculating tfidf for country "+country_code
			for term in text_collection.vocab().keys():
				print term
				print stopwords.words('english')
				sys.exit()
				if term not in stopwords.words('english') and term not in country_stopwords:
					tfidf[term] = text_collection.tf_idf(term, text_by_country[country_code])
			print sorted(tfidf.iteritems(), key=operator.itemgetter(1), reverse=True)[:50]
			sys.exit()

		# count country mentions
		if country_alpha3 is not None:
			people_counts = []
			all_people_counts = db.peopleMentioned(media_id_str, country_code)
			for name, count in sorted(all_people_counts.iteritems(), key=operator.itemgetter(1), reverse=True)[:15]:
				people_counts.append({
					'name': name, 'count':count
				})
			count_by_country.append({
				'alpha3': country_alpha3, 'count': count, 'people': people_counts
			})
			parsed_article_count += count
	info['countries'] = count_by_country
	info['articleCount'] = parsed_article_count
	output.append(info)

with open("output/data.json", "w") as text_file:
    text_file.write(json.dumps(output))
