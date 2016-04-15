;(function($, window, document, undefined) {

    var pluginName = 'epoch',
        defaults = {
            format: 'YYYY-MM-DD HH:mm:ss'
        }

    var Epoch = function(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.init();
    };

    Epoch.prototype = {

        init: function() {
            this.$element = $(this.element);
            
            /* set initial value */
            var value = this.$element.text();
            if ($.isNumeric(value))
                this.update(value);

            this.initEvents();

            return this;
        },

        initEvents: function() {
            this.$element.on('ws.update', $.proxy(this.update, this));
        },
        
        update: function(value) {
            if (!$.isNumeric(value))
                value = value.value;
            if (this.options.timezone)
                this.when = moment.tz(value * 1000, this.options.timezone);
            else
                this.when = moment.unix(value);
            this.humanize();
        },

        humanize: function() {
            if (!this.when)
                return;
            var human = this.when.format(this.options.format);
            if (this.$element.text() == human)
                return;
            this.$element.text(human);
            this.$element.show();
        }

    };

    $.fn[pluginName] = function(options) {
        return this.each(function() {
            if (!$.data(this, pluginName)) {
                $.data(this, pluginName, new Epoch(this, options));
            }
        });
    };

    $('[data-toggle="' + pluginName + '"]')[pluginName]();

})(jQuery, window, document);
