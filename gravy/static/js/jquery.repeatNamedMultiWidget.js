(function($) {

    var classname = 'repeat-named-multi-widget';
    var toggle = 'repeatNamedMultiWidget';
    var flag = 'createRepeatNamedMultiIndex';
    var selector = '.' + classname;

    // jQuery helper - find but stop descending branch when matched
    // TODO: make this a jQuery extension
    var findUntil = function(elem, s, matched) {
        matched = matched || $();
        elem.children().each(function() {
            elem = $(this);
            if (elem.is(s)) {
                matched.push(elem);
            } else {
                findUntil(elem, s, matched);
            }
        });
        return matched;
    };

    var repeatInit = function(elem) {
        $(elem[0].firstChild).click(function() {elem.remove();});
        elem.find('[data-toggle]').each(function() {
            var e = $(this);
            var init = e.data('toggle');
            e[init] && e[init]();
        });
    };

    // forms with repeatNamedMultiWigdets call this on submission so that
    // indexes can be filled out for input names.
    var addIndexes = function() {
        findUntil($(this), selector).each(function() {
            $(this).children('li').each(function(i) {
                var instance = $(this);
                instance.find(':input[name]').each(function() {
                    var e = $(this);
                    e.attr('name', e.attr('name').replace(/\[\]/, '[' + i + ']'));
                });
                addIndexes.call(this);
            });
        });
    };

    $.fn.extend({

        repeatNamedMultiWidget: function() {
            this.each(function() {

                var elem = $(this);
                var template = $(elem.data('repeatTemplate'));

                // add button
                elem.children('span').click(function () {
                    repeatInit(template.clone().insertBefore($(this)));
                });

                // remove button
                elem.children("li").children("span").click(function() {
                    $(this).closest("li").remove();
                });

                // create indexes on form submit (only create one event per form)
                var form = elem.closest('form');
                if (form.data(flag))
                    return;
                form.data(flag, true);
                form.submit(addIndexes);

            });
            return this;
        }

    });

    $(selector + ', [data-toggle="' + toggle + '"]').repeatNamedMultiWidget();


})(jQuery);
