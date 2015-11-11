/* datetimePicker */
(function($) {

    $.fn.extend({

        datetimePicker: function() {

			this.each(function() {
                var elem = $(this);
                var options = elem.data();
                // remove invalid options
                $.each(options, function(key, value) {
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
