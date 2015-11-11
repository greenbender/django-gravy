;(function($, window, document, undefined) {

    var pluginName = 'dateRangePicker',
        defaults = {
        };

    var DateRangePicker = function(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.init();
    };

    DateRangePicker.prototype = {

        init: function() {
            this.$element = $(this.element);
            this.$start = this.$element.find('input[type="text"][data-start]');
            this.$end = this.$element.find('input[type="text"][data-end]');
            this.$buttons = this.$element.find('button[data-value]');
            this.initButtons();
            return this;
        },

        initButtons: function() {
            this.$buttons.click($.proxy(this.click, this));
        },

        click: function(e) {
            var $button = $(e.target);
            var start = this.$start.data('DateTimePicker').date();
            if (start == null) {
                start = moment();
                this.$start.data('DateTimePicker').date(start);
            }
            var end = start.add($button.data('value'), 's');
            this.$end.data('DateTimePicker').date(end);
            e.preventDefault();
            return false;
        }
    };

    $.fn[pluginName] = function(options) {
        return this.each(function() {
            if (!$.data(this, pluginName)) {
                $.data(this, pluginName, new DateRangePicker(this, options));
            }
        });
    };

    $('[data-toggle="' + pluginName + '"]')[pluginName]();

})(jQuery, window, document);

