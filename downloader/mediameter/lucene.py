import datetime, json, time, urllib, urllib2, logging, sys
import xml.etree.ElementTree

class Lucene():

    SENTENCES_PER_PAGE = 10
    FAKE = False

    def __init__(self, start_date, end_date, media_id):
        self.log = logging.getLogger('mediameter')
        self.start_date = start_date
        self.end_date = end_date
        self.media_id = media_id

    def get_sentences(self, page):
        xml_response = self._query_lucene(self.SENTENCES_PER_PAGE, page*self.SENTENCES_PER_PAGE)
        if self.FAKE:
            xml_response = '<?xml version="1.0" encoding="UTF-8"?><response><lst name="responseHeader"><int name="status">0</int><int name="QTime">119</int><lst name="params"><str name="df">sentence</str><str name="start">1</str><str name="q">*</str><str name="fq">publish_date:[2013-09-01T00:00:00Z TO 2013-09-30T00:00:00Z] AND +media_id:1</str><str name="rows">10</str></lst></lst><result name="response" numFound="129966" start="1"><doc><str name="id">1767423501_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423501</str><str name="sentence">The pace of growth in the U.S. services sector accelerated in August to its fastest pace in almost eight years, an industry report showed on Thursday.</str><int name="sentence_number">1</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807551377409</long></doc><doc><str name="id">1767423502_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423502</str><str name="sentence">The Institute for Supply Management (ISM) said its services index rose to 58.6, its highest since December 2005, from 56 in July.</str><int name="sentence_number">2</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807551377410</long></doc><doc><str name="id">1767423503_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423503</str><str name="sentence">The reading handily topped economists\' consensus expectations for 55 and beat the high end of forecasts.</str><int name="sentence_number">3</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807633166337</long></doc><doc><str name="id">1767423504_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423504</str><str name="sentence">"Services represent approximately 85 percent of the economy, so the continued expansion of the sector is critical for the continuation of the overall economy recovery," wrote Thomas Simons, a money market economist at Jefferies &amp; Co in New York, in a note to clients.</str><int name="sentence_number">4</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807633166338</long></doc><doc><str name="id">1767423505_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423505</str><str name="sentence">In addition, U.S. private employers added 176,000 jobs in August, and new jobless claims last week fell to a near five-year low.</str><int name="sentence_number">5</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807633166339</long></doc><doc><str name="id">1767423506_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423506</str><str name="sentence">The data could help convince the Fed that the world\'s biggest economy is ready to stand on its own, able to withstand a pullback by policymakers on $85 billion per month in buying of Treasuries and mortgage-backed securities.</str><int name="sentence_number">6</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807633166340</long></doc><doc><str name="id">1767423507_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423507</str><str name="sentence">Yields on U.S. Treasuries jumped to 25-month highs backed views about slower Fed buying.</str><int name="sentence_number">7</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807634214912</long></doc><doc><str name="id">1767423508_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423508</str><str name="sentence">Stocks were on track for a third straight day of gains and the dollar notched multi-week peaks against the yen and the euro, fueled by the U.S. economic data.</str><int name="sentence_number">8</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807634214913</long></doc><doc><str name="id">1767423509_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423509</str><str name="sentence">Nevertheless, new orders for U.S. factory goods dropped in July by the most in four months, a worrisome sign for economic growth in the third quarter.</str><int name="sentence_number">9</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807634214914</long></doc><doc><str name="id">1767423543_ss</str><str name="field_type">ss</str><date name="publish_date">2013-09-05T19:09:12Z</date><int name="media_id">1</int><str name="story_sentences_id">1767423543</str><str name="sentence">The Commerce Department said new orders for manufactured goods dropped 2.4 percent.</str><int name="sentence_number">10</int><int name="stories_id">153713193</int><arr name="media_sets_id"><int>24</int><int>1</int><int>16959</int></arr><arr name="tags_id_media"><int>8874930</int><int>1</int><int>109</int><int>6729599</int><int>6071565</int><int>8875027</int></arr><long name="_version_">1447326807634214915</long></doc></result></response>'
        tree = xml.etree.ElementTree.fromstring(xml_response)
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

    def get_sentence_count(self):
        xml_response = self._query_lucene()
        if self.FAKE:
            xml_response = '<response><lst name="responseHeader"><int name="status">0</int><int name="QTime">122</int><lst name="params"><str name="df">sentence</str><str name="q">*</str><str name="fq">publish_date:[2013-09-01T00:00:00Z TO 2013-09-30T00:00:00Z] AND +media_id:1</str><str name="rows">0</str></lst></lst><result name="response" numFound="129966" start="0"></result></response>'
        tree = xml.etree.ElementTree.fromstring(xml_response)
        result_elt = tree.find('result')
        numFound = int(result_elt.attrib['numFound'])
        self.log.info("  found "+str(numFound)+" sentences")
        return numFound
