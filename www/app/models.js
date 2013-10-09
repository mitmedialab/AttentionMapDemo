
App.Country = Backbone.Model.extend({
    initialize: function(args){
        this.set({
            'id':ISO3166.getIdFromAlpha3(args['alpha3']),
            'alpha3':args['alpha3'],
            'name':ISO3166.getNameFromAlpha3(args['alpha3']),
            'centroid':Centroid.fromAlpha3(args['alpha3']),
            'pct': args['count'] / args['totalMediaArticles']
        });
    }
});

App.MediaSource = Backbone.Model.extend({
    initialize: function(args){
        this.set({
            'startDate': Date.parse(args['startDate']),
            'endDate': Date.parse(args['endDate'])
        });
        var countries = [];
        for(index in args['countries']){
            var countryInfo = args['countries'][index];
            countryInfo['totalMediaArticles'] = args['articleCount'];
            countries.push( new App.Country(countryInfo) );
        }
        this.set({'countries':countries});
    }
});

App.MediaSourceCollection = Backbone.Collection.extend({
    model: App.MediaSource,    
    initialize: function(){
    }
});
