;(function($, window, document, undefined) {

    var pluginName = 'dateRangePicker',
        defaults = {
            warnStartPast: false,
            warnDuration: false
        };

    var DateRangePicker = function(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.init();
    };

    DateRangePicker.prototype = {

        init: function() {
            this.$element = $(this.element);
            this.$start = this.$element.find('input[type="text"]').first().datetimePicker();
            this.startPicker = this.$start.data('DateTimePicker');
            this.$end = this.$element.find('input[type="text"]').last().datetimePicker();
            this.endPicker = this.$end.data('DateTimePicker');
            this.$buttons = this.$element.find('button[data-value]');
            this.initEvents();
            this.validate();
            return this;
        },

        initEvents: function() {
            this.$buttons.click($.proxy(this.click, this));
            this.$element.on('dp.change', $.proxy(this.validate, this));
        },

        validate: function() {
            var start = this.startPicker.date();
            var end = this.endPicker.date();
            var start_warn = 0;
            var end_warn = 0;
            if (this.options.warnStartPast && start) {
                if (start.add(this.options.warnStartPast, 'seconds') < moment()) {
                    start_warn++;
                }
            }
            if (this.options.warnDuration && start && end) {
                if (start.add(this.options.warnDuration, 'seconds') < end) {
                    start_warn++;
                    end_warn++;
                }
            }
            if (start_warn && !this.$start.hasClass('warning')) {
                this.$start.addClass('warning');
            }
            if (!start_warn && this.$start.hasClass('warning')) {
                this.$start.removeClass('warning');
            }
            if (end_warn && !this.$end.hasClass('warning')) {
                this.$end.addClass('warning');
            }
            if (!end_warn && this.$end.hasClass('warning')) {
                this.$end.removeClass('warning');
            }
        },

        click: function(e) {
            var $button = $(e.target);
            var start = this.startPicker.date();
            if (start == null) {
                start = moment();
                this.startPicker.date(start);
            }
            var end = start.add($button.data('value'), 's');
            this.endPicker.date(end);
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

