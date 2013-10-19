from mediameter.lucene import Lucene

start_date = '2013-09-01'
end_date = '2013-09-02'
media_id = 1

lucene = Lucene(start_date, end_date, media_id)

def file_to_string(file_path):
    str = None
    with open(file_path, "r") as myfile:
        str = ' '.join([line.replace('\n', '') for line in myfile.readlines()])
    return str

print "Testing sentence count parsing"
#wget "http://mcquery1.media.mit.edu:8983/solr/collection1/select?q=%2A&fq=publish_date%3A%5B2013-09-01T00%3A00%3A00Z+TO+2013-09-02T00%3A00%3A00Z%5D+AND+%2Bmedia_id%3A1&df=sentence&rows=0" -O sentencecount.xml
xml_text = file_to_string('mediameter/test/sentence-count.xml')
sentence_count = lucene._parse_sentence_count(xml_text)
assert (sentence_count==3900), "Sentence count is wrong (%r)" % sentence_count

print "Testing sentence parsing"
#
xml_text = file_to_string('mediameter/test/sentences.xml')
sentences = lucene._parse_sentences(xml_text)
assert len(sentences)==966, "Sentence count is wrong (%r)" % len(sentences)

print "Testing combining sentences into stories"
#
stories = lucene._parse_stories_from_sentences(sentences)
assert len(stories)==38, "Story count is wrong (%r)" % len(stories)
