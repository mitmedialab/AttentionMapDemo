import datetime, json, time, urllib, urllib2, logging, sys
import xml.etree.ElementTree

class Lucene():

    SENTENCES_PER_PAGE = 1000
    FAKE = False

    def __init__(self, start_date, end_date, media_id):
        self.log = logging.getLogger('mediameter')
        self.start_date = start_date
        self.end_date = end_date
        self.media_id = media_id

    def get_stories_from_sentences(self, page):
        sentences = self.get_sentences(page)
        return self._parse_stories_from_sentences(sentences)

    def _parse_stories_from_sentences(self, sentences):
        stories = {}
        for sentence in sentences:
            story_id = sentence['stories_id']
            if story_id not in stories:
                stories[story_id] = {
                    '_id': int(sentence['stories_id']),
                    'media_id': sentence['media_id'],
                    'sentences': {}
                }
            stories[story_id]['sentences'][sentence['sentence_number']] = sentence['sentence']
        return stories

    def get_sentences(self, page):
        xml_text = self._query_lucene(self.SENTENCES_PER_PAGE, page*self.SENTENCES_PER_PAGE)
        if self.FAKE:
            xml_text = self._file_to_string('mediameter/test/sentences.xml')
        return self._parse_sentences(xml_text)

    def _parse_sentences(self, xml_text):
        tree = xml.etree.ElementTree.fromstring(xml_text)
        sentences = []
        for doc in tree.findall(".//doc"):
            props = {
                'media_id': doc.find("./int[@name='media_id']").text,
                'story_sentences_id': doc.find("./str[@name='story_sentences_id']").text,
                'sentence': doc.find("./str[@name='sentence']").text,
                'sentence_number': doc.find("./int[@name='sentence_number']").text,
                'stories_id': doc.find("./int[@name='stories_id']").text               
            }
            sentences.append(props)
        return sentences

    def get_sentence_count(self):
        xml_text = self._query_lucene()
        if self.FAKE:
            xml_text = self._file_to_string('mediameter/test/sentence-count.xml')
        return self._parse_sentence_count(xml_text)
        
    def _parse_sentence_count(self, xml_text):
        tree = xml.etree.ElementTree.fromstring(xml_text)
        result_elt = tree.find('result')
        numFound = int(result_elt.attrib['numFound'])
        self.log.info("  found "+str(numFound)+" sentences")
        return numFound

    def _get_fq(self):
        return "publish_date:[%sT00:00:00Z TO %sT00:00:00Z] AND +media_id:%s" % (
                self.start_date, self.end_date, self.media_id
            )   

    def _query_lucene(self, rows=0, start=None):
        # http://lucene.apache.org/core/2_9_4/queryparsersyntax.html
        params = {
                'q':'*'
                , 'fq': self._get_fq()
                , 'rows':rows
                , 'df':'sentence'
            }
        if start is not None:
            params['start'] = start
        query = urllib.urlencode(params)
        url = 'http://mcquery1.media.mit.edu:8983/solr/collection1/select?%s' % (query)
        self.log.info("Querying Lucene: "+url)
        if not self.FAKE:
            return urllib2.urlopen(url).read()
        return None

    def _file_to_string(self, file_path):
        str = None
        with open(file_path, "r") as myfile:
            str = ' '.join([line.replace('\n', '') for line in myfile.readlines()])
        return str
