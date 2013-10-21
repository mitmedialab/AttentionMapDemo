import math
from mediacloud.storage import MongoStoryDatabase
from bson.code import Code

class ParseableStoryDatabase(MongoStoryDatabase):
    '''
    '''

    def saveNewStory(self, story):
        '''
        Need this because from Solr we don't get all the same fields as from the subset API
        '''
        self._saveStory(story)

    def updateStory(self, story_id, props):
        '''
        Need this because the regular client libary doesn't have a way to update stories :-(
        '''
        self._db.stories.update(
            { '_id':int(story_id) },
            { '$set': props }
        )

    def unparsedArticles(self, count=100):
        '''
        Return the last N stories without the "meta" property
        '''
        results = self._db.stories.find({"meta":{'$exists': False}}).limit(count)
        stories = []
        for item in results:
            stories.append(item)
        return stories

    def storyCountByMediaSource(self):
        '''
        Returns dict of media_id_str=>story_count
        '''
        key = ['media_id']
        condition = {}
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        raw_results = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(raw_results,'media_id')

    def storyCountByCountry(self, media_id=None):
        key = ['meta.primaryCountries']
        condition = None
        if media_id is not None:
            condition = {'media_id': media_id}
        initial = {'value':0}
        reduce = Code("function(doc,prev) { prev.value += 1; }") 
        raw_results = self._db.stories.group(key, condition, initial, reduce);
        return self._resultsToDict(raw_results,'meta.primaryCountries')

    def peopleMentioned(self, media_id, country_alpha2=None):
        mapper = Code("""
               function () {
                 var countryCode = '"""+country_alpha2+"""';
                 var mediaId = '"""+media_id+"""';
                 if( (this.media_id==mediaId) && (this.meta.primaryCountries.indexOf(countryCode) > -1) ){
                   for(var idx in this.meta.people){
                     var name = this.meta.people[idx]['name'];
                     emit(name, 1);
                    }
                 }
               }
               """)
        reducer = Code("""
                function (key, values) {
                  var total = 0;
                  for (var i = 0; i < values.length; i++) {
                    total += values[i];
                  }
                  return total;
                }
                """)
        results = self._db.stories.map_reduce(mapper,reducer, "peopleMentionedInMediaCountry")
        docs = []
        for doc in results.find():
            docs.append(doc)
        return self._resultsToDict(docs,'_id')   

    def mediaStories(self, media_id, country_alpha2=None):
        criteria = { 'media_id': media_id }
        if country_alpha2 is not None:
            criteria = {'meta.primaryCountries': country_alpha2}
        docs = []
        for doc in self._db.stories.find(criteria):
            docs.append(doc)
        return docs

    # assumes key is integer!
    def _resultsToDict(self, raw_results, id_key):
        ''' 
        Helper to change a key-value set of results into a python dict
        '''
        results = {}
        for doc in raw_results:
            key_ok = False
            try:
                # first make sure key is an integer
                throwaway = doc[id_key]
                # now check optional range
                if throwaway=='?' or throwaway=='NULL':
                    key_ok = False
                else:
                    key_ok = True
            except:
                # we got NaN, so ignore it
                key_ok = False
            if key_ok:
                key_to_use = doc[id_key]
                if isinstance(key_to_use, list):
                    if len(key_to_use)==0:
                        key_to_use = None
                    else:
                        key_to_use = key_to_use[0]
                if key_to_use is not None:
                    results[ key_to_use ] = int(doc['value'])
        return results
