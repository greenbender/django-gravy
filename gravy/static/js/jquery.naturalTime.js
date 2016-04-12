;(function($, window, document, undefined) {

    var pluginName = 'naturalTime',
        defaults = {
            locale: 'en',
            interval: 1
        },
        locales = {
            'en': {
                isUpdate: true,
                relativeTime: {
                    future: 'in %s',
                    past:   '%s ago',
                    s:  '%d seconds',
                    m:  'a minute',
                    mm: '%d minutes',
                    h:  'an hour',
                    hh: '%d hours',
                    d:  'a day',
                    dd: '%d days',
                    M:  'a month',
                    MM: '%d months',
                    y:  'a year',
                    yy: '%d years'
                },
            },
            'en-deadline': {
                parentLocale: 'en',
                relativeTime: {
                    future: 'in %s',
                    past:   '%s overdue',
                    s:  '%d seconds',
                    m:  'a minute',
                    mm: '%d minutes',
                    h:  'an hour',
                    hh: '%d hours',
                    d:  'a day',
                    dd: '%d days',
                    M:  'a month',
                    MM: '%d months',
                    y:  'a year',
                    yy: '%d years'
                }
            }
        };

    /* add locales to moment */
    $.each(locales, function(name, locale) {
        if (locale.isUpdate) {
            delete locale.isUpdate;
            moment.updateLocale(name, locale);
        } else {
            moment.defineLocale(name, locale);
        }
    });

    var NaturalTime = function(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.options.interval *= 1000;
        this.init();
    };

    NaturalTime.prototype = {

        init: function() {
            this.$element = $(this.element);
            
            /* set initial value */
            var value = this.$element.text();
            if ($.isNumeric(value))
                this.update(value);

            this.initEvents();
            this.poll();

            return this;
        },

        initEvents: function() {
            this.$element.on('ws.update', $.proxy(this.update, this));
        },
        
        update: function(value) {
            if (!$.isNumeric(value))
                value = value.value;
            this.then = moment.utc(value * 1000).locale(this.options.locale);
        },

        humanize: function() {
            if (!this.then)
                return;
            var human = this.then.fromNow();
            if (this.$element.text() == human)
                return;
            this.$element.text(human);
        },

        poll: function() {
            if (!$.contains(document, this.element))
                return;
            this.humanize();
            setTimeout($.proxy(this.poll, this), this.options.interval);
        }

    };

    $.fn[pluginName] = function(options) {
        return this.each(function() {
            if (!$.data(this, pluginName)) {
                $.data(this, pluginName, new NaturalTime(this, options));
            }
        });
    };

    $('[data-toggle="' + pluginName + '"]')[pluginName]();

})(jQuery, window, document);
