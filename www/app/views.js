
App.MediaMapView = Backbone.View.extend({
	tagName: 'div',
	className: 'am-media-map',
	template: _.template($('#am-media-map-template').html()),
	initialize: function(){
		this.id = "am-media-map-"+this._getMediaId();
		_.bindAll(this, 'changeMediaId', 'handleValidCountryClick')
 		App.globals.eventMgr.bind("changeMediaSource", this.changeMediaId);
        // init with first media source
        this.options.currentMediaId = this.options.mediaSources.at(0).get('mediaId');
        this.render();
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
        App.debug("Changing to media id "+mediaId);
    	this.options.currentMediaId = mediaId;
        this._renderMapCountries();
        $('.media-source-name').text(this._getCurrentMediaSource().get('mediaName'));
        
        /* CSD - CHANGE AND PUT THIS SOMEWHERE ELSE MORE BACKBONEY??? */
        if(this.map.selectedCountry != null){
            this.map.selectedCountryID = this.map.selectedCountry.id; 
            this.map.selectedCountryName = this.map.selectedCountry.get('name'); 
        }

        this.map.selectedCountry = this._getCurrentMediaSource().attributes.countries._byId[this.map.selectedCountryID];
        

        this.countryFocus = new App.MediaMapCountryFocusView({
                'country': this.map.selectedCountry,
                'name':this.map.selectedCountryName,

        });
        /*$('.media-source-name').animate({'opacity': 0.1}, 1000, function () {
          $('.media-source-name').text(this._getCurrentMediaSource().get('mediaName'));
        }).animate({'opacity': 1}, 1000);*/
        
    },
	_getMediaId: function(){
		return this._getCurrentMediaSource().get('mediaId');
	},
    _getCurrentMediaSource: function(){
        return this.options.mediaSources.get(this.options.currentMediaId);
    },
    handleValidCountryClick: function(country) {
        var g = this.map.svg.select('g');
        var x, y, k;
        var that = this;
        
        this.mouseoverView.hide();

        if (country && this.map.selectedCountry !== country) {
            // zoom in on a country
            var path = App.globals.countryIdToPath[country.get('id')];
            var centroid = App.globals.mediaMap.map.path.centroid(path.geometry);
            x = centroid[0];
            y = centroid[1];
            k = 4;
            this.map.selectedCountry = country;
            this.countryFocus = new App.MediaMapCountryFocusView({
                'country': country,
            });
        } else {
            // zoom out again
            x = App.globals.mediaMap.map.width / 2;
            y = App.globals.mediaMap.map.height / 2;
            k = 1;
            this.map.selectedCountry = null;
            this.countryFocus.clear();
        }
        g.selectAll("path").classed("active", this.map.selectedCountry && function(country) { return country === that.map.selectedCountry; });
        g.transition()
            .duration(750)
            .attr("transform", "translate(" + this.map.width / 2 + "," + this.map.height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
            .style("stroke-width", 1 / k + "px");
    },
    _initMap: function(){
        var width = 1170;
        var height = 645;
        var map = {
			'container': this.$('.am-world-map').get()[0],
        	'width': width,
       		'height': height,
            'scale': 225,
        	'projection': null,
        	'svg': null,
        	'maxWeight': null,
        	'color': null,
        	'opacity': null
        };
        map.projection = d3.geo.kavrayskiy7()
            .scale(map.scale)
            .translate([width / 2, height / 2]);
        map.path = d3.geo.path().projection(map.projection);
        map.svg = d3.select(map.container).append("svg")
            .attr("width", map.width)
            .attr("height", map.height);


        //zooming stuff
        map.svg.append("rect")
            .attr("class", "background")
            .attr("width", map.width)
            .attr("height", map.height)
            .on("click", this.handleValidCountryClick);

        var g = map.svg.append("g");
        g.append('g').attr('id', 'am-background');
        g.append('g').attr('id', 'am-data');

        //end zooming stuff
        
        map.maxWeight = d3.max(this._getCurrentMediaSource().get("countries").models, function (d) { return d.get('count'); });
        map.color = d3.scale.log()
            .range([App.config.colors.minColor, App.config.colors.maxColor])
            .domain([1, map.maxWeight]);
        map.opacity = d3.scale.pow().exponent(2)
            .range([0, 1])
            .domain([0, map.maxWeight]);
        map.selectedCountry = null;
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
            .attr('stroke-width', 0.5)
            .attr("d", this.map.path);

    },
    _renderMapCountries: function() {
        var that = this;
        g = this.map.svg.select('#am-data')
            .selectAll('.am-country')
            .data(this._getCurrentMediaSource().get("countries").models, function (d) { return d.get('id'); });
        g.enter()
            .append("path")
            .attr("class", "am-country")
            .attr("fill", App.config.colors.disabledColor)
            .attr('stroke', App.config.colors.outline)
            .attr('stroke-width', 0.5)
            .attr("id", function(d,i) {return "am-country"+d.get('id')})
            .attr("data-id", function(d,i) {return d.id})
            .attr("d", function (d) { return that.map.path(App.globals.countryIdToPath[d.get('id')]); })
            .on("click", function (d) { return that.handleValidCountryClick(d); })
            .on("mousemove", function (d) { return that.handleValidCountryMouseover(d); })
            .on("mouseout", function (d) { return that.handleValidCountryMouseout(d); });
        g.exit()
            .attr("class", "am-country")
            .transition().duration(1500)
            .style("fill-opacity", 1e-6)
            .remove();
        g.transition()
            .duration(1500)
            .attr("fill", function (d) {return that.map.color(d.get('count'));} );
        
    },
    handleValidCountryMouseover: function(country) {
        if (this.mouseoverView == null || country!=this.mouseoverView.options.country){
            this.mouseoverView = new App.MediaMapMouseoverView({
                'country': country,
            });
        } else {
            this.mouseoverView.show();
        }
    },
    handleValidCountryMouseout: function(country) {
        this.mouseoverView.hide()
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
        	this.$('ul').append(itemView.el);
            if (this.options['mediaSources'][idx].id == this.options['currentMediaId']){
                itemView.$el.addClass('active');
            }
        }
    }
});

App.MediaPickerItemView = Backbone.View.extend({
    tagName: 'li',
    className: 'am-media-picker-item',
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
        this.$el.addClass('active');
        this.$el.siblings().removeClass('active')
    	App.debug("switch to media "+mediaId);
    	App.globals.eventMgr.trigger("changeMediaSource",mediaId);
    }
});

App.MediaMapMouseoverView = Backbone.View.extend({
    el: $("#mouseover-info-window"),
    template: _.template($('#am-media-map-mouseover-template').html()),
    initialize: function(){
        this.render();
    },
    render: function(){
        var country = this.options.country.get('alpha3');
        var fill = $('#am-data>.am-country[data-id="'+this.options.country.id+'"]').attr("fill");
        
        var count = this.options.country.get('count');
        var content = this.template({
            country: this.options.country.get('name'),
            num_articles: count,
            attention: ((count > App.globals.mediaMap.map.maxWeight/10) ? "Higher attention" : (count > App.globals.mediaMap.map.maxWeight/100) ? "Medium Attention" : "Lower Attention"),
            country_color: "color:"+fill

        });
        this.$el.html( content );
        this.show();
    },
    hide: function(){
        this.$el.hide();
    },
    show: function(){
        var coord = d3.mouse(d3.select("svg").node());
        d3.select(this.$el.get(0)).style("left", coord[0] + 20  + "px" );
        d3.select(this.$el.get(0)).style("top", coord[1] + 10 + "px");
        if (!this.$el.is(':visible')){this.$el.show()};
    }
});
App.MediaMapCountryFocusView = Backbone.View.extend({
    el: $("#country-focus"),
    template: _.template($('#country-focus-template').html()),
    initialize: function(){
        this.render();
    },
    render: function(){
        var country = this.options.country;
        if (country == null){
            country = App.globals.mediaMap.selectedCountry;
            var content = this.template({
                country: this.options.name,
                numArticles: 0,
                mediaSource: App.globals.mediaMap._getCurrentMediaSource().get('mediaName'),
                attention: "No attention",
                country_color: "color:#666",
                people: "No people data available"
            });

        } else {
            country = country.get('alpha3');
            var fill = $('#am-data>.am-country[data-id="'+this.options.country.id+'"]').attr("fill");
            
            var count = this.options.country.get('count');
            var peopleCountMax = d3.max(this.options.country.get('people'), function(d) { return d.count; });
            var fontSizeScale = d3.scale.linear()
                .range([10, 24])
                .domain([1, peopleCountMax]);
            var peopleHash = this.options.country.get('peopleHash');
            var peopleNames = _.map( _.keys(this.options.country.get('peopleHash')), 
                function(item){ 
                    item = peopleHash[item];
                    var peopleHtml;
                    
                    
                    
                    if (item['name'].indexOf(" ") > 2 ){
                        peopleHtml = '<span style="font-size:'+ fontSizeScale(item['count']) +'px"><a target="_blank" href="http://en.wikipedia.org/wiki/'+ item['name'].replace(" ", "_") +'">'+ item['name'] + '</a></span>';
                    } else{
                        peopleHtml = '<span style="font-size:'+ fontSizeScale(item['count']) +'px">'+ item['name'] + '</span>';
                    }
                    
                    return peopleHtml;
                }).join(", ");
            var content = this.template({
                country: this.options.country.get('name'),
                numArticles: count,
                mediaSource: App.globals.mediaMap._getCurrentMediaSource().get('mediaName'),
                attention: ((count > App.globals.mediaMap.map.maxWeight/10) ? "Higher attention" : "Lower Attention"),
                country_color: "color:"+fill,
                people: peopleNames
            });
        }
        
        App.debug()
        this.$el.html( content );
        $('.am-media-map h3').fadeOut();
        this.$el.fadeIn();

    },
    clear: function(){
        this.$el.empty();
        this.$el.hide();
        $('.am-media-map h3').fadeIn();
    }
   
});
