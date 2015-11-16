/* fileInput */
(function($) {

    var fileDesc = function(elem) {
        i = $(elem)[0];
        if (!i.files || !i.files.length)
            return '';
        if (i.files.length == 1)
            return i.files[0].name;
        return i.files.length + ' files selected';
    };


    var defaults = {
        label: null,
        icon: 'glyphicon-open',
        buttonPos: 'after',
        wrapper:
            '<div class="input-group">' +
                '<span class="input-group-btn">' +
                    '<span class="btn btn-default btn-file"></span>' +
                '</span>' +
            '</div>'
    };

    var input = $('<input>', {type: 'text', class: 'form-control', readonly:true});

    $.fn.extend({

        fileInput: function(options) {

            options = $.extend(true, defaults, options || {});

            this.change(function() {
                var elem = $(this);
                elem.closest('.input-group').find(':text').val(fileDesc(elem));
            }).wrap(options.wrapper);

            if (options.buttonPos == 'before') {
                this.closest('.input-group-btn').after(input.clone());
            } else {
                this.closest('.input-group-btn').before(input.clone());
            }

            if (options.icon)
                this.before($('<span>', {'class': 'glyphicon ' + options.icon}));

            if (options.label)
                this.before(options.label);

            return this;

        }

    });

    $('[data-toggle="fileInput"]').fileInput();

})(jQuery);

