
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

App.CountryCollection = Backbone.Collection.extend({
    model: App.Country,
    initialize: function(){
    },
    getMaxPct: function(){
        return _.max(this.models, function(country){
            return country.get('pct');
        }).get('pct');
    }
});

App.MediaSource = Backbone.Model.extend({
    initialize: function(args){
        this.set({
            'startDate': Date.parse(args['startDate']),
            'endDate': Date.parse(args['endDate']),
            'id': args['mediaId']
        });
        for(index in args['countries']){
            args['countries'][index]['totalMediaArticles'] = args['articleCount'];
        }
        this.set( {'countries': new App.CountryCollection(args['countries']) });
    }
});

App.MediaSourceCollection = Backbone.Collection.extend({
    model: App.MediaSource,    
    initialize: function(){
    }
});
