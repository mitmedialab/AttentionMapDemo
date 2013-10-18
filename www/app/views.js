
App.MediaMapView = Backbone.View.extend({
	tagName: 'div',
	className: 'am-media-map',
	template: _.template($('#am-media-map-template').html()),
	initialize: function(){
		this.id = "am-media-map-"+this._getMediaId();
		this.render();
		_.bindAll(this, 'changeMediaId')
 		App.globals.eventMgr.bind("changeMediaSource", this.changeMediaId);
	},
	render: function(){
		var content = this.template({
			name: this._getCurrentMediaSource().get('mediaName')
		});
        this.$el.html( content );	// need to do this *before* adding the map so the d3.select works right
        this._initMap();
        this._renderMapBackground();
        this._renderMapCountries();
    },
    changeMediaId: function(mediaId){
    	this.options.currentMediaId = mediaId;
        this._renderMapCountries();
    },
	_getMediaId: function(){
		return this._getCurrentMediaSource().get('mediaId');
	},
    _getCurrentMediaSource: function(){
        return this.options.mediaSources.get(this.options.currentMediaId);
    },
    _initMap: function(){
        var map = {
			'container': this.$('.am-world-map').get()[0],
        	'width': 550,
       		'height': 300,
        	'scale': 130,
        	'offset': [260,180],
        	'projection': null,
        	'svg': null,
        	'maxWeight': null,
        	'color': null,
        	'opacity': null
        };
        map.projection = d3.geo.kavrayskiy7()
            .scale(map.scale)
            .translate([map.offset[0], map.offset[1]])
            .precision(.1);
        map.path = d3.geo.path().projection(map.projection);
        map.svg = d3.select(map.container).append("svg")
            .attr("width", map.width)
            .attr("height", map.height);
        map.svg.append('g').attr('id', 'am-background');
        map.svg.append('g').attr('id', 'am-data');
        map.maxWeight = d3.max(this._getCurrentMediaSource().get("countries").models, function (d) { return d.get('count'); });
        map.color = d3.scale.linear()
            .range([App.config.colors.minColor, App.config.colors.maxColor])
            .domain([0, map.maxWeight]);
        map.opacity = d3.scale.pow().exponent(2)
            .range([0, 1])
            .domain([0, map.maxWeight]);
        this.map = map;	// save all the map stuff on this object
	},
    _renderMapBackground: function() {
        var world = App.globals.worldMap;
        var countries = topojson.feature(world, world.objects.countries).features;
        var country = this.map.svg.select('#am-background').selectAll(".am-country").data(countries);
        country.enter().append("path")
            .attr("class", 'am-country')
            .attr("data-id",function(d){ return d.id })
            .attr('fill', App.config.colors.disabledColor)
            .attr('stroke', App.config.colors.outline)
            .attr("d", this.map.path);
    },
    _renderMapCountries: function() {
        var that = this;
        var g = this.map.svg.select('#am-data')
            .selectAll('.am-country')
            .data(this._getCurrentMediaSource().get("countries").models, function (d) { return d.get('id'); });
        g.enter()
            .append("path")
            .attr("class", "am-country")
            .attr("fill", App.config.colors.disabledColor)
            .attr("id", function(d,i) {return "am-country"+d.get('id')})
            .attr("data-id", function(d,i) {return d.id})
            .attr("d", function (d) { return that.map.path(App.globals.countryIdToPath[d.get('id')]); })
            /*.on("click", function (d) { return that.handleValidCountryClick(d); })*/;
        g.exit()
            .remove();
        g.transition()
            .attr("fill", function (d) {return that.map.color(d.get('count'));} );
    }
});

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
        	this.$('div.btn-group-vertical').append(itemView.el);
        }
    }
});

App.MediaPickerItemView = Backbone.View.extend({
    tagName: 'button',
    className: 'btn btn-default am-media-picker-item',
    template: _.template($('#am-media-picker-item-template').html()),
    events: {
    	"click	"	:    "handleClick"
    },
    initialize: function(){
    },
    render: function(){
		var content = this.template({
			id: this.options.mediaSource.get('mediaId'),
			name: this.options.mediaSource.get('mediaName')
		});
        this.$el.attr('type','button');
        this.$el.html( content );
    },
    handleClick: function(){
    	var mediaId = this.options.mediaSource.get('mediaId');
    	App.debug("switch to media "+mediaId);
    	App.globals.eventMgr.trigger("changeMediaSource",mediaId);
    }
});
