import sys, time, logging, ConfigParser, json
from mediameter.lucene import Lucene
from mediameter import parser
from mediameter.db import ParseableStoryDatabase
from iso3166 import countries
import mediacloud.api
import operator
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
#from nltk.corpus import stopwords
import string, math

DO_IF_IDF = True

start_time = time.time()
# adapted from http://www.ai.mit.edu/projects/jmlr/papers/volume5/lewis04a/a11-smart-stop-list/english.stop
english_stop_words = ["``", "mr.", "ms.", "/a", "href=", "...", "--", "target=", "'s", "n't", \
	"a","a's","able","about","above","according","accordingly","across","actually","after","afterwards","again","against","ain't","all","allow","allows","almost","alone","along","already","also","although","always","am","among","amongst","an","and","another","any","anybody","anyhow","anyone","anything","anyway","anyways","anywhere","apart","appear","appreciate","appropriate","are","aren't","around","as","aside","ask","asking","associated","at","available","away","awfully","b","be","became","because","become","becomes","becoming","been","before","beforehand","behind","being","believe","below","beside","besides","best","better","between","beyond","both","brief","but","by","c","c'mon","c's","came","can","can't","cannot","cant","cause","causes","certain","certainly","changes","clearly","co","com","come","comes","concerning","consequently","consider","considering","contain","containing","contains","corresponding","could","couldn't","course","currently","d","definitely","described","despite","did","didn't","different","do","does","doesn't","doing","don't","done","down","downwards","during","e","each","edu","eg","eight","either","else","elsewhere","enough","entirely","especially","et","etc","even","ever","every","everybody","everyone","everything","everywhere","ex","exactly","example","except","f","far","few","fifth","first","five","followed","following","follows","for","former","formerly","forth","four","from","further","furthermore","g","get","gets","getting","given","gives","go","goes","going","gone","got","gotten","greetings","h","had","hadn't","happens","hardly","has","hasn't","have","haven't","having","he","he's","hello","help","hence","her","here","here's","hereafter","hereby","herein","hereupon","hers","herself","hi","him","himself","his","hither","hopefully","how","howbeit","however","i","i'd","i'll","i'm","i've","ie","if","ignored","immediate","in","inasmuch","inc","indeed","indicate","indicated","indicates","inner","insofar","instead","into","inward","is","isn't","it","it'd","it'll","it's","its","itself","j","just","k","keep","keeps","kept","know","knows","known","l","last","lately","later","latter","latterly","least","less","lest","let","let's","like","liked","likely","little","look","looking","looks","ltd","m","mainly","many","may","maybe","me","mean","meanwhile","merely","might","more","moreover","most","mostly","much","must","my","myself","n","name","namely","nd","near","nearly","necessary","need","needs","neither","never","nevertheless","new","next","nine","no","nobody","non","none","noone","nor","normally","not","nothing","novel","now","nowhere","o","obviously","of","off","often","oh","ok","okay","old","on","once","one","ones","only","onto","or","other","others","otherwise","ought","our","ours","ourselves","out","outside","over","overall","own","p","particular","particularly","per","perhaps","placed","please","plus","possible","presumably","probably","provides","q","que","quite","qv","r","rather","rd","re","really","reasonably","regarding","regardless","regards","relatively","respectively","right","s","said","same","saw","say","saying","says","second","secondly","see","seeing","seem","seemed","seeming","seems","seen","self","selves","sensible","sent","serious","seriously","seven","several","shall","she","should","shouldn't","since","six","so","some","somebody","somehow","someone","something","sometime","sometimes","somewhat","somewhere","soon","sorry","specified","specify","specifying","still","sub","such","sup","sure","t","t's","take","taken","tell","tends","th","than","thank","thanks","thanx","that","that's","thats","the","their","theirs","them","themselves","then","thence","there","there's","thereafter","thereby","therefore","therein","theres","thereupon","these","they","they'd","they'll","they're","they've","think","third","this","thorough","thoroughly","those","though","three","through","throughout","thru","thus","to","together","too","took","toward","towards","tried","tries","truly","try","trying","twice","two","u","un","under","unfortunately","unless","unlikely","until","unto","up","upon","us","use","used","useful","uses","using","usually","uucp","v","value","various","very","via","viz","vs","w","want","wants","was","wasn't","way","we","we'd","we'll","we're","we've","welcome","well","went","were","weren't","what","what's","whatever","when","whence","whenever","where","where's","whereafter","whereas","whereby","wherein","whereupon","wherever","whether","which","while","whither","who","who's","whoever","whole","whom","whose","why","will","willing","wish","with","within","without","won't","wonder","would","would","wouldn't","x","y","yes","yet","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves","z","zero"]

config = ConfigParser.ConfigParser()
config.read('downloader.config')

# connect to database
db = ParseableStoryDatabase(config.get('mongo','db_name'),config.get('mongo','host'),int(config.get('mongo','port')))

output = []	# the thing to jsonify at the end

def count_incidence(lookup, term):
	if term in lookup:
		lookup[term] += 1
	else:
		lookup[term] = 1

def add_idf(idf, term, count):
	idf[term] = count

# get list of all media sources
print "Starting to generate json"
media_counts = db.storyCountByMediaSource()
for media_id_str, story_count in media_counts.iteritems():
	print "  Working on media "+media_id_str
	info = {
		'mediaId': int(media_id_str),
		'totalArticleCount': story_count,
		'mediaName': mediacloud.api.mediaSource(media_id_str)['name']
	}

	# setup tfidf computation
	doc_by_country = {}			# maps alpha2 to country nltk.Text
	term_doc_incidence = {}		# maps term to number of country nltk.Text's it appears in
	idf = {}					# maps term to inverse document frequency
	if DO_IF_IDF:
		print "    Computing TF and IDF"
		country_counts = db.storyCountByCountry(media_id_str)
		total_countries = len(country_counts)
		for country_code, count in country_counts.iteritems():
			# fetch and put back together the stories
			print "      fetch "+country_code,
			country_stories = db.mediaStories(media_id_str, country_code)
			print "("+str(len(country_stories))+"), ",
			print "create text, ",
			country_stories_text = ' '.join( [ ' '.join( story['sentences'].values() )  for story in country_stories] ) # this feels dumb
			# nltk-ize it
			print "nltk, ",
			doc = nltk.Text([ \
				word.encode('utf-8') \
					for sent in sent_tokenize(country_stories_text.lower()) for word in word_tokenize(sent) \
					if word not in english_stop_words and word not in string.punctuation])
			# compute the document tf 
			print "doc tf ",
			doc_term_count = len(doc.vocab().keys())
			print "        ("+str(doc_term_count)+" terms)"
			doc_by_country[country_code] = doc
		print "      computing df"
		[count_incidence(term_doc_incidence,term) \
			for country_doc in doc_by_country.values() \
			for term in country_doc.vocab().keys() ]
		print "		  done "
		print "       computing idf"
		idf = { term: math.log(float(total_countries)/float(incidence)) for term, incidence in term_doc_incidence.iteritems() }
		print "		  done "
		print "    done setting up text collection for media "+media_id_str

	# now create results we care about
	print "    Computing info for each country"
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
			print '      Unknown country code '+country_code
			country_alpha3 = None			
		
		tfidf_results = []
		if DO_IF_IDF:
			# compute document term frequency for stories about this country from this media source
			print "      Calculating tfidf for country "+country_code
			doc_tf = doc_by_country[country_code].vocab()
			tfidf = { term: frequency * idf[term] for term, frequency in doc_tf.iteritems() }
			print "       done"
			tfidf_results = [ {'term': term, 'count':freq} \
				for term, freq in sorted(tfidf.iteritems(), key=operator.itemgetter(1), reverse=True)]\
				[:30]

		# put country-specific info together
		if country_alpha3 is not None:
			all_people_counts = db.peopleMentioned(media_id_str, country_code)
			people_counts = [ { 'name': name, 'count':count } \
				for name, count in sorted(all_people_counts.iteritems(), key=operator.itemgetter(1), reverse=True)]\
				[:30]
			count_by_country.append({
				'alpha3': country_alpha3, 'count': count, 'people': people_counts, 'tfidf': tfidf_results
			})
			parsed_article_count += count

	info['countries'] = count_by_country
	info['articleCount'] = parsed_article_count
	output.append(info)

print "Writing output"
with open("output/data.json", "w") as text_file:
    text_file.write(json.dumps(output))

print "  done (in "+str(time.time() - start_time)+" seconds)"
