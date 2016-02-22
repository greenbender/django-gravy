/* XXX: this is terrible it is highly coupled with html classes of 'unrelated'
 * elements */
(function($) {

    $.fn.extend({

        dependsWidget: function() {
            this.each(function() {

                var $elem = $(this);
                var $dependants = $elem.closest('.form-group').siblings().wrapAll('<div/>').parent();

                if (!$elem[0].checked)
                    $dependants.hide();

                $elem.change(function() {
                    if (this.checked)
                        $dependants.show(200);
                    else
                        $dependants.hide(200);
                });

            });
            return this;
        }

    });

    $('.depends-widget').dependsWidget();

})(jQuery);
