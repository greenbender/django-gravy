;(function($, window, document, undefined) {

    var pluginName = 'simpleMap',
        defaults = {
            interval: 60,
            center: [133.25, -24.81],
            zoom: 3,
            marker: 'marker.png',
            colours: [
                '#e6194B', '#3cb44b', '#4363d8', '#f58231',
                '#911eb4', '#42d4f4', '#f032e6', '#bfef45',
                '#fabebe', '#ffe119', '#469990', '#e6beff',
                '#9A6324', '#fffac8', '#800000', '#aaffc3',
                '#808000', '#ffd8b1', '#000075'
            ],
            template:
                '<div>Timestamp: {timestamp}</div>' +
                '<div>Source: {sourceName}</div>' +
                '<div>Location: {latitude}, {longitude}</div>' +
                '<div>Accuracy: {accuracy}</div>'
        };

    /* helpers */
    var _format = function(fmt, args) {
        return fmt.replace(/{([^}]+)}/g, function(match, lookup) {
            return typeof args[lookup] != 'undefined'
                ? args[lookup]
                : match;
        });
    };

    var SimpleMap = function(element, options) {
        if (typeof OpenLayers === 'undefined') {
            console.log("Requires OpenLayers");
            return;
        }
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.options.interval *= 1000;
        if (typeof this.options.tileUrl == 'string')
            this.options.tileUrl = [this.options.tileUrl];
        this.init();
    };

    SimpleMap.prototype = {

        init: function() {
            this.$element = $(this.element);
            this.initMap();
            if (this.options.interval) {
                this.poll();
            } else {
                this.update();
            }
            return this;
        },

        initMap: function() {
            var that = this;
            
            // style
            this.style = new OpenLayers.Style(
                {
                    strokeWidth: '${stroke}',
                    fillOpacity: '${opacity}',
                    fontFamily: '"Helvetica Neue",Helvetica,Arial,sans-serif',
                    fontColor: '#333',
                    fontSize: '10px',
                    externalGraphic: this.options.marker,
                    graphicOpacity: 1,
                    graphicWidth: 30,
                    graphichHeight: 48,
                    graphicXOffset: -15,
                    graphicYOffset: -24,
                    strokeColor: '${colour}',
                    fillColor: '${colour}',
                }
            ); 

            // map
            this.map = new OpenLayers.Map({div: this.element});

            // disable doubleclick navigation
            this.map.addControl(new OpenLayers.Control.Navigation({
                defaultDblClick: function() {return;}
            }));

            // layers
            this.layers = {
                osm: new OpenLayers.Layer.OSM('OpenStreetMap', this.options.tileUrl),
                vector: new OpenLayers.Layer.Vector('Vector', {
                    styleMap: new OpenLayers.StyleMap(this.style),
                    eventListeners: {            
                        featureover: $.proxy(this.over, this),
                        featureout: $.proxy(this.out, this),
                        featureclick: $.proxy(this.click, this),
                        nofeatureclick: $.proxy(this.zoom, this),
                        featureremoved: $.proxy(this.out, this)
                    }
                })
            };
            $.each(this.layers, function(name, layer) {
                that.map.addLayer(layer);
            });

            // default transform
            this.transform = {
                source: new OpenLayers.Projection('EPSG:4326'),
                dest: this.map.getProjectionObject()
            };

            // set map center
            this.map.setCenter(this._lonLat(this.options.center), this.options.zoom);
        },

        _lonLat: function() {
            var lon, lat;
            if (arguments.length == 1) {
                lon = arguments[0][0];
                lat = arguments[0][1];
            } else {
                lon = arguments[0];
                lat = arguments[1];
            }
            return new OpenLayers.LonLat(lon, lat).transform(
                this.transform.source,
                this.transform.dest
            );
        },

        _point: function() {
            var lonlat = this._lonLat.apply(this, arguments);
            return new OpenLayers.Geometry.Point(lonlat.lon, lonlat.lat);
        },

        _opacity_from_timestamp: function(ts) {
            var age_hrs = Math.floor(moment().diff(moment(ts)) / (1000 * 60 * 60));
            if (age_hrs < 1)
                return 0.5;
            if (age_hrs < 6)
                return 0.4;
            if (age_hrs < 24)
                return 0.3;
            if (age_hrs < (24 * 7))
                return 0.2;
            return 0.1;
        },

        zoom: function() {
            if (this.layers.vector.features.length)
                this.map.zoomToExtent(this.layers.vector.getDataExtent());
        },

        click: function(e) {
            var feature = e.feature;
            if (feature.data.type == 'mark') {
                geometry = feature.data.area.geometry;
            } else {
                geometry = feature.geometry;
            }
            this.map.zoomToExtent(geometry.getBounds());
            return false;
        },

        over: function(e) {
            var feature = e.feature;
            if (feature.popup || feature.data.type != 'mark')
                return true;
            var popup = new OpenLayers.Popup.FramedCloud(
                'featurePopup',
                feature.geometry.getBounds().getCenterLonLat(),
                null, _format(this.options.template, feature.data),
                null, false, null
            );
            feature.popup = popup;
            this.map.addPopup(popup);
            return true;
        },

        out: function(e) {
            var feature = e.feature;
            if (!feature.popup || feature.data.type != 'mark')
                return true;
            this.map.removePopup(feature.popup);
            feature.popup.destroy();
            feature.popup = null;
            return true;
        },

        polygon: function(i, polygon) {
            var that = this;
            var points = [];
            $.each(polygon.points, function(_, point) {
                points.push(that._point(point));
            });
            var ring = new OpenLayers.Geometry.LinearRing(points);
            var poly = new OpenLayers.Geometry.Polygon([ring]);
            var area = new OpenLayers.Feature.Vector(poly, {
                type: 'area',
                colour: polygon.colour || that.options.colours[i % that.options.colours.length],
                stroke: polygon.stroke || (typeof polygon.accuracy === 'undefined') ? 0 : 1,
                opacity: polygon.opacity || that._opacity_from_timestamp(polygon.timestamp)
            });
            var cent = this._point(polygon.longitude, polygon.latitude);
            var mark = new OpenLayers.Feature.Vector(cent, {
                type: 'mark',
                longitude: polygon.longitude.toFixed(4),
                latitude: polygon.latitude.toFixed(4),
                timestamp: polygon.timestamp,
                fromNow: moment(polygon.timestamp).fromNow(),
                accuracy: polygon.accuracy || 'unknown',
                sourceName: polygon.source.name,
                area: area
            });
            this.layers.vector.addFeatures([area, mark]);
        },

        update: function() {
            var that = this;
            $.get(this.options.polyUrl, function(data) {
                that.layers.vector.removeAllFeatures();
                that.layers.vector.destroyFeatures();
                $.each(data.result.polygons, $.proxy(that.polygon, that));
                if (data.result.polygons.length > 0)
                    that.zoom();
            });
        },

        poll: function() {
            if (!$.contains(document, this.element))
                return;
            this.update();
            setTimeout($.proxy(this.poll, this), this.options.interval);
        }

    };

    $.fn[pluginName] = function(options) {
        return this.each(function() {
            if (!$.data(this, pluginName)) {
                $.data(this, pluginName, new SimpleMap(this, options));
            }
        });
    };

})(jQuery, window, document);
