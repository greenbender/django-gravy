(function($) {

    var locales = {
        'en': {
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

    $.each(locales, moment.locale);

    var defaults = {
        locale: 'en',
        interval: 1
    };

    var humanize = function(elem) {
        var then = elem.data('then');
        if (!then)
            return;
        var human = then.fromNow();
        if (elem.text() == human)
            return;
        elem.text(human);
    }

    var update = function(elem, value, locale) {
        var then = moment.utc(value * 1000).locale(locale);
        elem.data('then', then);
    };

    $.fn.extend({

        naturalTime: function(options) {

            this.each(function() {

                var elem = $(this);
                var options = $.extend({}, defaults, options, elem.data());
                options.interval *= 1000;

                // initial update 
                if ($.isNumeric(elem.text())) {
                    update(elem, elem.text(), options.locale);
                    humanize(elem);
                }

                // update on ws.update
                elem.on('ws.update', function(e) {
                    update(elem, e.value, options.locale);
                });

                // polling update
                setInterval(function() {humanize(elem);}, options.interval);

            });

            return this;
        }

    });

    $('[data-toggle="naturalTime"]').naturalTime();

})(jQuery);
