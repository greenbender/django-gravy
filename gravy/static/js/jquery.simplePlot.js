;(function($, window, document, undefined) {

    var pluginName = 'simplePlot',
        defaults = {
            interval: 0,
        };

    /* helpers */
    var _format = function(fmt, args) {
        return fmt.replace(/{([^}]+)}/g, function(match, lookup) {
            return typeof args[lookup] != 'undefined'
                ? args[lookup]
                : match;
        });
    };

    var SimplePlot = function(element, options, $them) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.options.interval *= 1000;
        if (this.options.hoverTipFormat === undefined)
            this.options.hoverTipFormat = [];
        else if (typeof this.options.hoverTipFormat == 'string')
            this.options.hoverTipFormat = [this.options.hoverTipFormat];
        this.$them = $them;
        this.init();
    };

    SimplePlot.prototype = {

        init: function() {
            this.$element = $(this.element);
            this.$hoverTip = $('<span class="plottip" style="position:absolute;"></span>');
            this._panned = false;
            this._zoomTimeout;
            this._sequence = 0;

            this.initEvents();
            this.update();
            if (this.options.interval)
                this.poll();

            return this;
        },

        initEvents: function() {
            this.$element.on('plotpan', $.proxy(this.plotpan, this));
            this.$element.on('plotzoom', $.proxy(this.plotzoom, this));
            this.$element.on('mouseup', $.proxy(this.mouseup, this));
            this.$element.on('plothover', $.proxy(this.plothover, this));
        },

        cloneAxis: function() {
            var srcPlot = this.$element.data('plot');
            if (!srcPlot)
                return;
            var srcOpts = srcPlot.getAxes().xaxis.options;
            this.$them.each(function() {
                var dstPlot = $(this).data('plot');
                if (!dstPlot)
                    return;
                var dstOpts = dstPlot.getAxes().xaxis.options;
                dstOpts.min = srcOpts.min;
                dstOpts.max = srcOpts.max;
                dstPlot.setupGrid();
                dstPlot.draw();
            });
        },

        plotzoom: function(e, plot, args) {
            var that = this;
            this.cloneAxis();
            this._sequence++;

            // rate limit updates
            clearTimeout(this._zoomTimeout);
            this._zoomTimeout = setTimeout(function() {
                that.update({propagate:true});
            }, 200);
        },

        plotpan: function(e, plot, args) {
            this.cloneAxis();
            this._panned = true;
        },

        mouseup: function(e) {
            if (this._panned && e.button == 0) {
                this._panned = false;
                this._sequence++;
                this.update({propagate:true});
            }
        },

        plothover: function(e, position, item) {
            if (item === null) {
                this.$hoverTip.remove();
            } else {
                var format = this.options.hoverTipFormat[item.seriesIndex];
                if (format) {
                    var text = _format(format, {
                        value: item.series.data[item.dataIndex][1]
                    });
                    this.$hoverTip.text(text);
                    this.$hoverTip.appendTo(this.$element.parent());
                    this.$hoverTip.offset({
                        left: item.pageX - this.$hoverTip.outerWidth() / 2,
                        top: item.pageY - this.$hoverTip.outerHeight() - 5
                    });
                }
            }
        },

        update: function(args) {
            var that = this;
            var params = {};

            // get params
            if (args && args.limits) {
                params = args.limits;
            } else {
                var plot = this.$element.data('plot');
                if (plot) {
                    var axis = plot.getAxes().xaxis;
                    params = {
                        xmin: Math.floor(axis.min),
                        xmax: Math.ceil(axis.max)
                    }
                }
            }

            params.sequence = this._sequence;
            
            $.get(this.options.url, params, function(data) {
                if(data.sequence == that._sequence)
                    $.plot(that.$element, data.series, data.options);
            });

            // fire for them
            if (args && args.propagate) {
                delete args.propagate;
                this.$them.each(function() {
                    var p = $(this).data('simplePlot');
                    p && p.update(args);
                });
            }
        },

        poll: function() {
            if (!$.contains(document, this.element))
                return;
            var plot = this.$element.data('plot');
            if (plot) {
                var axis = plot.getAxes().xaxis,
                    min = Math.floor(axis.min),
                    max = Math.ceil(axis.max),
                    datamax = Math.ceil(axis.datamax);
                if (datamax <= max) {
                    this.update({
                        limits: {
                            xmin: min + this.options.interval,
                            xmax: max + this.options.interval
                        }
                    });
                }
            }
            setTimeout($.proxy(this.poll, this), this.options.interval);
        }

    };

    $.fn[pluginName] = function(options) {
        var $that = this;
        return this.each(function() {
            var $them = $that.not($(this));
            if (!$.data(this, pluginName)) {
                $.data(this, pluginName, new SimplePlot(this, options, $them));
            }
        });
    };

})(jQuery, document, window);


;(function($, window, document, undefined) {

    var pluginName = 'simplePiePlot',
        defaults = {
            interval: 0,
            hoverTipFormat: '{label} {percent}%',
            hoverTipQueryField: 'label'
        };

    var _lookup = function(args, name) {
        var parts = name.split(/\.(.+)?/, 2);
        var value = args[parts[0]];
        if (typeof value == 'undefined' || parts.length == 1)
            return value;
        return _lookup(value, parts[1]);
    };

    var _format = function(fmt, args) {
        return fmt.replace(/{([^}]+)}/g, function(match, lookup) {
            var value = _lookup(args, lookup);
            return typeof value != undefined ? value : match;
        });
    };

    /* helpers */
    var labelFormatter = function(label, series) {
        return '<span class="plottip">' + label + '</span>';
    };

    var SimplePiePlot = function(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.options.interval *= 1000;
        if (!this.options.hoverTipQueryParam)
            this.options.hoverTipQueryParam = this.options.hoverTipQueryField;
        this.init();
    };

    SimplePiePlot.prototype = {

        init: function() {
            this.$element = $(this.element);
            this.$hoverTip = $('<span class="plottip" style="position:absolute;"></span>');
            this._sequence = 0;
            this._hoverTipQueryValue = null;

            this.initEvents();
            this.update();
            if (this.options.interval)
                this.poll();

            return this;
        },

        initEvents: function() {
            this.$element.on('plothover', $.proxy(this.plothover, this));
        },

        plothover: function(e, position, item) {
            if (!this.options.hoverTipUrl)
                return;

            if (item === null) {
                this.$hoverTip.remove();
                this._hoverTipQueryValue = null;
                return;
            }
            
            var value = item.series[this.options.hoverTipQueryField];
            if (this._hoverTipQueryValue == value) {
                this.$hoverTip.offset({
                    left: position.pageX - this.$hoverTip.outerWidth() / 2,
                    top: position.pageY - this.$hoverTip.outerHeight() - 5
                });
                return;
            }
            this._hoverTipQueryValue = value;

            var params = {};
            params[this.options.hoverTipQueryParam] = value;

            var that = this;
            $.get(this.options.hoverTipUrl, params, function(data) {
                if (!data.result) {
                    that.$hoverTip.remove();
                    return;
                }
                var format = that.options.hoverTipFormat;
                if (format) {
                    var text = _format(format, data.result);
                    if (that.options.hoverTipHtml) {
                        that.$hoverTip.html(text);
                    } else {
                        that.$hoverTip.text(text);
                    }
                    that.$hoverTip.appendTo(that.$element.parent());
                    that.$hoverTip.offset({
                        left: position.pageX - that.$hoverTip.outerWidth() / 2,
                        top: position.pageY - that.$hoverTip.outerHeight()
                    });
                }
            });
        },

        update: function(args) {
            var that = this;
            var params = {};

            params.sequence = this._sequence;
            
            $.get(this.options.url, params, function(data) {
                if(data.sequence == that._sequence) {
                    data.options.series.pie.label.formatter = labelFormatter;
                    $.plot(that.$element, data.data, data.options);
                }
            });
        },

        poll: function() {
            var plot = this.$element.data('plot');
            if (plot) {
                this.update();
            }
            setTimeout($.proxy(this.poll, this), this.options.interval);
        }

    };

    $.fn[pluginName] = function(options) {
        return this.each(function() {
            if (!$.data(this, pluginName)) {
                $.data(this, pluginName, new SimplePiePlot(this, options));
            }
        });
    };

})(jQuery, document, window);
