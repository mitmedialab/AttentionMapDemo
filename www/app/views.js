
App.MediaMapView = Backbone.View.extend({
    tagName: 'div',
    className: 'am-media-map',
    template: _.template($('#am-media-map-template').html()),
    initialize: function(){
        this.id = "am-media-map-"+this._getMediaId();
        _.bindAll(this, 'changeMediaId', 'changeTopic', 'handleValidCountryClick')
         App.globals.eventMgr.bind("changeMediaSource", this.changeMediaId);
         App.globals.eventMgr.bind("changeTopic", this.changeTopic);
        // init with first media source
        this.options.currentMediaId = this.options.mediaSources.at(0).get('mediaType');
        this.render();
    },
    render: function(){
        var content = this.template({
            name: this._getCurrentMediaSource().get('name')
        });
        this.$el.html( content );    // need to do this *before* adding the map so the d3.select works right
        this._initMap();
        this._renderMapBackground();
        this._renderMapCountries();
    },
    changeMediaId: function(mediaType){
        App.debug("Changing to media id "+mediaType);
        this.options.currentMediaId = mediaType;
        this._renderMapCountries();
        $('.media-source-name').text(this._getCurrentMediaSource().get('name'));
        
        /* CSD - CHANGE AND PUT THIS SOMEWHERE ELSE MORE BACKBONEY??? */
        if(this.map.selectedCountry != null){
            this.map.selectedCountryID = this.map.selectedCountry.id; 
            this.map.selectedCountryName = this.map.selectedCountry.get('name'); 
        }

        this.map.selectedCountry = this._getCurrentMediaSource().attributes.countries._byId[this.map.selectedCountryID];
        
        if(this.map.selectedCountry != null){
            this.countryFocus = new App.MediaMapCountryFocusView({
                    'country': this.map.selectedCountry,
                    'name':this.map.selectedCountryName,

            });
        }
    },
        
    changeTopic: function(topic){
        App.debug("Changing to topic "+topic);
        this.options.currentTopic = topic;
        this._renderMapCountries();
        
        /* CSD - CHANGE AND PUT THIS SOMEWHERE ELSE MORE BACKBONEY??? */
        if(this.map.selectedCountry != null){
            this.map.selectedCountryID = this.map.selectedCountry.id; 
            this.map.selectedCountryName = this.map.selectedCountry.get('name'); 
        }

        this.map.selectedCountry = this._getCurrentMediaSource().attributes.countries._byId[this.map.selectedCountryID];
        
        if(this.map.selectedCountry != null){
            this.countryFocus = new App.MediaMapCountryFocusView({
                    'country': this.map.selectedCountry,
                    'name':this.map.selectedCountryName,

            });
        }
    },
    _getMediaId: function(){
        return this._getCurrentMediaSource().get('mediaType');
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
            this.map.selectedCountryID = null;
            this.countryFocus.clear();
        }
        g.selectAll("path").classed("active", this.map.selectedCountry && function(country) { return country === that.map.selectedCountry; });
        g.transition()
            .duration(750)
            .attr("transform", "translate(" + this.map.width / 2 + "," + this.map.height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
            .style("stroke-width", 1 / k + "px");
    },
    _initMap: function(){
        var parentWidth = $('#am-media-map').width();
        var width = parentWidth;
        var height = width/1.8;
        this.$('.am-world-map').height(height);
        var map = {
            'container': this.$('.am-world-map').get()[0],
            'width': width,
               'height': height,
            'scale': width/5.2,
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
        map.topicColor = d3.scale.log()
            .range([App.config.colors.minColor, App.config.colors.maxColor])
            .domain([1, 100]);
        map.opacity = d3.scale.pow().exponent(2)
            .range([0, 1])
            .domain([0, map.maxWeight]);
        map.selectedCountry = null;
        this.map = map;    // save all the map stuff on this object
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
            .attr("fill", function (d) {
                if (that.options.currentTopic == 'All Topics') {
                    return that.map.color(d.get('count'));
                }
                var count = _.find(
                        JSON.parse(d.get('topics_field'))
                        , function (d) {
                            return d.topic == that.options.currentTopic;
                        }
                    ).value / 100 * 99 + 1;
                return that.map.topicColor(count);
            });
        
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
    },
    addCommas: function(nStr)
    {
      nStr += '';
      x = nStr.split('.');
      x1 = x[0];
      x2 = x.length > 1 ? '.' + x[1] : '';
      var rgx = /(\d+)(\d{3})/;
      while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
      }
      return x1 + x2;
    },
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
        "click    "    :    "handleClick"
    },
    initialize: function(){
    },
    render: function(){
        var content = this.template({
            id: this.options.mediaSource.get('mediaType'),
            name: this.options.mediaSource.get('name')
        });
        this.$el.attr('type','button');
        this.$el.html( content );
    },
    handleClick: function(){
        var mediaType = this.options.mediaSource.get('mediaType');
        this.$el.addClass('active');
        this.$el.siblings().removeClass('active')
        App.debug("switch to media "+mediaType);
        App.globals.eventMgr.trigger("changeMediaSource",mediaType);
    }
});

App.TopicPickerView = Backbone.View.extend({
    el: $("#am-topic-picker"),
    template: _.template($('#am-topic-picker-template').html()),
    topics: [ 'All Topics', 'Arts', 'Economy', 'Health', 'Politics', 'Science', 'Sports' ],
    
    initialize: function(){
        this.render();
    },
    render: function(){
        this.$el.html( this.template() );
        for(idx in this.topics){
            var itemView = new App.TopicPickerItemView({
                'topic': this.topics[idx]
            });
            itemView.render();
            this.$('ul').append(itemView.el);
            if (this.topics[idx] == this.options['currentTopic']) {
                itemView.$el.addClass('active');
            }
        }
    }
});

App.TopicPickerItemView = Backbone.View.extend({
    tagName: 'li',
    className: 'am-topic-picker-item',
    template: _.template($('#am-topic-picker-item-template').html()),
    events: {
        "click    "    :    "handleClick"
    },
    initialize: function(){
    },
    render: function(){
        var content = this.template({
            topic: this.options.topic
        });
        this.$el.attr('type','button');
        this.$el.html( content );
    },
    handleClick: function(){
        this.$el.addClass('active');
        this.$el.siblings().removeClass('active')
        App.debug("switch to topic "+this.options.topic);
        App.globals.eventMgr.trigger("changeTopic",this.options.topic);
    }
});

App.MediaMapMouseoverView = Backbone.View.extend({
    el: $("#am-mouseover-info-window"),
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
            num_articles: App.globals.mediaMap.addCommas(count),
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
       
        var offset = ($(window).width() - $("svg").width())/2;
        d3.select(this.$el.get(0)).style("left", coord[0] + 10 + offset + "px" );
        d3.select(this.$el.get(0)).style("top", coord[1] + 12 + "px");
        if (!this.$el.is(':visible')){this.$el.show()};
    }
});
App.MediaMapCountryFocusView = Backbone.View.extend({
    el: $("#am-country-focus"),
    template: _.template($('#am-country-focus-template').html()),
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
                mediaType: App.globals.mediaMap._getCurrentMediaSource().get('mediaType'),
                name: App.globals.mediaMap._getCurrentMediaSource().get('name'),
                attention: "No attention",
                country_color: "color:#666",
                people: "No people data available"
            });

        } else {
            country = country.get('alpha3');
            var fill = $('#am-data>.am-country[data-id="'+this.options.country.id+'"]').attr("fill");
            var articleCount = this.options.country.get('count');
            // assemble html for list of people
            var peopleCountMax = d3.max(this.options.country.get('people'), function(d) { return d.count; });
            var peopleFontSizeScale = d3.scale.linear()
                .range([10, 24])
                .domain([1, peopleCountMax]);
            var peopleHash = this.options.country.get('peopleHash');
            var peopleHtml = _.map( this.options.country.get('people'), 
                function(item){ 
                    var html;
                    if (item['name'].indexOf(" ") > 2 ){
                        html = '<span style="font-size:'+ peopleFontSizeScale(item['count']) +'px"><a target="_blank" href="http://en.wikipedia.org/wiki/'+ item['name'].replace(" ", "_") +'">'+ item['name'].replace("+"," ") + '</a></span>';
                    } else{
                        html = '<span style="font-size:'+ peopleFontSizeScale(item['count']) +'px">'+ item['name'].replace("+"," ") + '</span>';
                    }
                    return html;
                }).join(", ");
            // assemble html for list of keywords
            var keywordCountMax = d3.max(this.options.country.get('tfidf'), function(d) { return d.count; });
            var keywordCountMin = d3.min(this.options.country.get('tfidf'), function(d) { return d.count; });
            var keywordFontSizeScale = d3.scale.linear()
                .range([10, 24])
                .domain([keywordCountMin, keywordCountMax]);
            //filter keywords for messiness like quotes & dashes
            var keywordHtml = _.map( _.filter(this.options.country.get('tfidf'), function(item){
                    var k = item["term"];
                    return k!= "–" && k!="•" && k!= "”" && k!=" " && k !=" ``"&& k !="``" && k != "''" && k !="'s" && k != "--" && k != "n't" && k !="—";
            } ), function(item){
                        return '<span style="font-size:'+ keywordFontSizeScale(item['count']) +'px">'+ item['term'] + '</span>';
                }).join(", ");

            // render
            var content = this.template({
                country: this.options.country.get('name'),
                numArticles: App.globals.mediaMap.addCommas(articleCount),
                mediaType: App.globals.mediaMap._getCurrentMediaSource().get('mediaType'),
                name: App.globals.mediaMap._getCurrentMediaSource().get('name'),
                attention: ((articleCount > App.globals.mediaMap.map.maxWeight/10) ? "Higher attention" : "Lower Attention"),
                country_color: "color:"+fill,
                people: peopleHtml,
                keywords: keywordHtml
            });
        
            // Create donut chart
            var el = this.el;
            var topicData = JSON.parse(this.options.country.get('topics_field'));
            nv.addGraph(function() {
                var chart = nv.models.pieChart()
                    .x(function(d) { return d.topic })
                    .y(function(d) { return d.value })
                    .showLabels(true)     //Display pie labels
                    .labelThreshold(.05)  //Configure the minimum slice size for labels to show up
                    .labelType("percent") //Configure what type of data to show in the label. Can be "key", "value" or "percent"
                    .donut(true)          //Turn on Donut mode. Makes pie chart look tasty!
                    .donutRatio(0.35)     //Configure how big you want the donut hole size to be.
                    ;
        
                d3.select(el).select(".viz svg")
                    .datum(topicData)
                    .transition().duration(350)
                    .call(chart);
                
                return chart;
            });
        }
        
        this.$el.html( content );
        $('.am-media-map h3').fadeOut();
        this.$el.fadeIn();

    },
    clear: function(){
        this.$el.empty();
        this.$el.hide();
        $('.am-media-map h3').fadeIn();
    },
    
   
});
