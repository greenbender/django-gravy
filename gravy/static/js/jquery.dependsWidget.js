(function($) {

    var classname = 'depends-widget';
    var selector = '.' + classname;

    $.fn.extend({

        dependsWidget: function() {
            this.each(function() {

                var $elem = $(this);
                var $children = $elem.children('li');
                var $first = $children.first();
                var $enable = $first.find('input[type="checkbox"]');
                var $dependants = $children.not($first);
                delete $children;
                delete $first;

                $dependants.hide();

                $enable.change(function() {
                    if (this.checked)
                        $dependants.show(200);
                    else
                        $dependants.hide(200);
                });

            });
            return this;
        }

    });

    $(selector).dependsWidget();

})(jQuery);
