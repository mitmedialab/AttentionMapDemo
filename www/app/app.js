
// namespaced wrapper around all our application's code
window.App = {

    config: {
        writeLog: true
    },

    // wrapper so we can turn off logging in one place
    debug: function(str){
        if(App.config.writeLog){
            console.log(str);
        }
    },

	initialize: function(){
		App.debug("Initializing App");
		ISO3166.initialize();
        var runApp = _.after(1,App.run);
        App.allMediaSources = new App.MediaSourceCollection();
        // kick off all async loading
        App.allMediaSources.fetch({
            url: "data/data.json",
            success: runApp
        });
	},

    run: function(){
        App.debug('Run App');
        App.mediaPicker = new App.MediaPickerView({
            'mediaSources': App.allMediaSources.models
        });
    }

};
