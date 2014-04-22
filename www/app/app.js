
// namespaced wrapper around all our application's code
window.App = {

    config: {
        writeLog: true,
        colors: {
            minColor: 'rgb(241,233,187)',
            maxColor: 'rgb(207,97,35)',
            disabledColor: 'rgb(180, 180, 180)',
            enabledColor: 'rgb(243,195,99)',
            outline: 'rgb(100,100,100)'
        }
    },

    globals: {
        worldMap: null,         // reusable topojson
        countryIdToPath: null,  // lookup from country numeric id to path element
        eventMgr: null,         // global event aggregator (http://stackoverflow.com/questions/10042124/backbone-js-global-events)
        allMediaSources: null,  // collection of the data loaded
        mediaPicker: null,      // singleton media picker
        mediaMap: null,         // singleton media map
    },

    // wrapper so we can turn off logging in one place
    debug: function(str){
        if(App.config.writeLog){
            console.log(str);
        }
    },

	initialize: function(){
        App.globals.eventMgr = _.extend({}, Backbone.Events);
		$('#am-progress-bar').show();
        App.debug("Initializing App");
		ISO3166.initialize();
        var runApp = _.after(2,App.run);
        App.globals.allMediaSources = new App.MediaSourceCollection();
        // kick off all async loading
        App.globals.allMediaSources.fetch({
            url: "data/geostudy-data.json",
            success: runApp
        });
        d3.json('data/world-110m.json', function(data){
            App.globals.worldMap = data;
            App.globals.countryIdToPath = {};
            var countries = topojson.feature(App.globals.worldMap, App.globals.worldMap.objects.countries).features;
            $.each(countries, function (i, d) {
                App.globals.countryIdToPath[d.id] = d;
            });
            runApp();
        });
	},

    run: function(){
        App.debug('Run App');
        $('#am-progress-bar').hide();
        App.globals.mediaPicker = new App.MediaPickerView({
            'currentMediaId':App.globals.allMediaSources.models[0].id,
            'mediaSources': App.globals.allMediaSources.models
        });
        // create all the maps
        App.globals.mediaMap = new App.MediaMapView({'currentMediaId':App.globals.allMediaSources.models[0].id, 'mediaSources':App.globals.allMediaSources});
        $('#am-media-map').append(App.globals.mediaMap.el);
        
    },


};
