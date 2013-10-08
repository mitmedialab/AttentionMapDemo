
App.Country = Backbone.Model.extend({
    initialize: function(args){
        this.set({
            'id':ISO3166.getIdFromAlpha3(args['code']),
            'alpha3':args['code'],
            'name':ISO3166.getNameFromId(this.get('id')),
            'centroid':Centroid.fromAlpha3(args['code'])
        });
        // count has the number of articles about this country
    }
});

App.MediaSource = Backbone.Model.extend({
    initialize: function(args){
        this.set({
            'startDate': Date.parse(args['startDate']),
            'endDate': Date.parse(args['endDate'])
        });
        var countries = [];
        for(country in countries){
            country['totalArticles']
            countries.push( new App.Country(country) );
        }
        this.set({'countries':countries});
    }
});

App.MediaSourceCollection = Backbone.Collection.extend({
    model: App.MediaSource,    
    initialize: function(){
    }
});
