/* datetimePicker */
(function($) {

    var keyBinds = $.fn.datetimepicker.defaults.keyBinds;
    var unbind = ['up', 'down', 'control up', 'control down', 'left', 'right', 'pageUp', 'pageDown', 'delete', 'enter'];
    $.each(unbind, function(i, u) { delete keyBinds[u]; });

    $.fn.extend({

        datetimePicker: function() {

			this.each(function() {
                var elem = $(this);
                var options = elem.data();
                // remove invalid options
                $.each(options, function(key, value) {
                    if (key == 'DateTimePicker')
                        return;
                    if ($.fn.datetimepicker.defaults[key] === undefined)
                        delete options[key];
                });
                elem.datetimepicker(options);
            });

            return this;
        }

    });

    $('[data-toggle=datetimePicker]').datetimePicker();

})(jQuery);
