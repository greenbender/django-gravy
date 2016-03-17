;(function($, window, document, undefined) {

    var pluginName = 'simpleMap',
        defaults = {
            interval: 60,
            center: [133.25, -24.81],
            zoom: 3,
            marker: 'marker.png',
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
                    strokeWidth: 1,
                    fillOpacity: 0.3,
                    fontFamily: '"Helvetica Neue",Helvetica,Arial,sans-serif',
                    fontColor: '#333',
                    fontSize: '10px',
                    externalGraphic: this.options.marker,
                    graphicOpacity: 1,
                    graphicWidth: 30,
                    graphichHeight: 48,
                    graphicXOffset: -15,
                    graphicYOffset: -24
                },
                {
                    rules: [
                        new OpenLayers.Rule({
                            filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: 'sourceId',
                                value: 1
                            }),
                            symbolizer: {
                                strokeWidth: 0,
                                fillColor: '#0fba1f'
                            }
                        }),
                        new OpenLayers.Rule({
                            filter: new OpenLayers.Filter.Comparison({
                                type: OpenLayers.Filter.Comparison.EQUAL_TO,
                                property: 'sourceId',
                                value: 2
                            }),
                            symbolizer: {
                                strokeColor: '#207cdb',
                                fillColor: '#207cdb'
                            }
                        })
                    ]
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

        polygon: function(polygon) {
            var that = this;
            var points = [];
            $.each(polygon.points, function(_, point) {
                points.push(that._point(point));
            });
            var ring = new OpenLayers.Geometry.LinearRing(points);
            var poly = new OpenLayers.Geometry.Polygon([ring]);
            var area = new OpenLayers.Feature.Vector(poly, {
                type: 'area',
                sourceId: polygon.source.id
            });
            var cent = this._point(polygon.longitude, polygon.latitude);
            var mark = new OpenLayers.Feature.Vector(cent, {
                type: 'mark',
                longitude: polygon.longitude.toFixed(4),
                latitude: polygon.latitude.toFixed(4),
                timestamp: polygon.timestamp,
                accuracy: polygon.accuracy,
                sourceName: polygon.source.name,
                sourceId: polygon.source.id,
                area: area
            });
            this.layers.vector.addFeatures([area, mark]);
        },

        update: function() {
            var that = this;
            $.get(this.options.polyUrl, function(data) {
                that.layers.vector.removeAllFeatures();
                that.layers.vector.destroyFeatures();
                $.each(data.result.polygons, function(_, polygon) {
                    that.polygon(polygon);
                });
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
