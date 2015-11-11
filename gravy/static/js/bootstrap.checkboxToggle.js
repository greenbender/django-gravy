/* checkboxToggle */
(function($) {

    var prefix = 'id-cb-toggle-';
    var idx = 0;

    $.fn.extend({

        checkboxToggle: function() {

			this.each(function() {

                if (!this.id)
                    this.id = prefix + idx++;
                $(this).after($('<label>', {for: this.id}));

            });

            return this;
        }

    });

    $('[data-toggle="checkboxToggle"]').checkboxToggle();

})(jQuery);
