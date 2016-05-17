;(function($, window, document, undefined) {

    var pluginName = 'dateRangePicker',
        defaults = {};

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
            this.$info = this.$element.find('.info');
            this.initEvents();
            this.updateInfo();
            return this;
        },

        initEvents: function() {
            this.$buttons.click($.proxy(this.click, this));
            this.$element.on('dp.change', $.proxy(this.updateInfo, this));
        },

        updateInfo: function() {
            var start = this.startPicker.date();
            var end = this.endPicker.date();
            if (start) {
                var html = 'Start <strong>' + start.locale('en').fromNow() + '</strong>';
                if (end) {
                    html += ' for <strong>'
                    var diff = end.diff(start);
                    var duration = moment.duration(Math.abs(diff));
                    var hours = Math.floor(duration.asHours());
                    var minutes = duration.minutes();
                    if (diff < 0) html += '-'
                    if (hours) html += hours + 'h'
                    if (minutes || !hours) html += (hours ? ' ':'') + minutes + 'm'
                    if (end.isBefore()) {
                        html += '<span class="text-danger"> Ends in the past!</span>';
                    }
                    html += '</strong>'
                }
                this.$info.html(html);
            } else {
                this.$info.html('&nbsp;');
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

