
App.MediaPickerView = Backbone.View.extend({
    el: $("#am-media-picker"),
    template: _.template($('#am-media-picker-template').html()),
    initialize: function(){
    	this.render();
    },
    render: function(){
    	this.$el.html( this.template() );
        for(idx in this.options['mediaSources']){
        	var itemView = new App.MediaPickerItemView({
        		'mediaSource': this.options['mediaSources'][idx]
        	});
        	itemView.render();
        	this.$('ul').append(itemView.el);
        }
    }
});

App.MediaPickerItemView = Backbone.View.extend({
    tagName: 'li',
    className: 'am-media-picker-item',
    template: _.template($('#am-media-picker-item-template').html()),
    initialize: function(){
    },
    render: function(){
		var content = this.template({
			id: this.options.mediaSource.get('mediaId'),
			name: this.options.mediaSource.get('mediaName')
		});
        this.$el.html( content );
    }
});
