(function($) {
    if (moment) {
        var options = $('body').data();
        if (options.momentjsFormat)
            moment.defaultFormat = options.momentjsFormat;
        if (moment.tz && options.momentjsTimezone)
            moment.tz.setDefault(options.momentjsTimezone);
    }
})(jQuery);
