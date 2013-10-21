import sys, time, logging, ConfigParser, json
from mediameter import parser
from mediameter.db import ParseableStoryDatabase
from iso3166 import countries
import mediacloud.api

config = ConfigParser.ConfigParser()
config.read('downloader.config')

# connect to database
db = ParseableStoryDatabase(config.get('mongo','db_name'),config.get('mongo','host'),int(config.get('mongo','port')))

output = []	# the thing to jsonify at the end

# get list of all media sources
media_counts = db.storyCountByMediaSource()
for media_id_str, story_count in media_counts.iteritems():
	info = {
		'mediaId': int(media_id_str),
		#'articleCount': story_count,
		'mediaName': mediacloud.api.mediaSource(media_id_str)['name']
	}
	count_by_country = []
	geocoded_article_count = 0
	for country_code, count in db.storyCountByCountry(media_id_str).iteritems():
		alpha3 = None
		try:
			country_iso3166 = countries.get(country_code)
			alpha3 = country_iso3166.alpha3
		except KeyError:
			# not sure how to handle things that aren't fully approved, like XK for Kosovo :-(
			print 'Unknown country code '+country_code
			alpha3 = None
		if alpha3 is not None:
			count_by_country.append({
				'alpha3': alpha3, 'count': count
			})
			geocoded_article_count += count
	info['countries'] = count_by_country
	info['articleCount'] = geocoded_article_count
	output.append(info)

with open("output/data.json", "w") as text_file:
    text_file.write(json.dumps(output))
