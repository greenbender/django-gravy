;(function($, window, document, undefined) {
    
    var pluginName = 'terminal',
        defaults = {
            prompt: '>',
            historyKey: 'term.history',
            reverseSearchPrompt: '(reverse-i-search)`{term}\':'
        },
        template = $(
            '<div class="cmd">' +
            '    <div class="request">' +
            '        <span class="prompt"></span><span class="cmdline"></span>' +
            '    </div>' +
            '    <pre class="response"></pre>' +
            '</div>'
        );

    /* helpers */
    var _format = function(fmt, args) {
        return fmt.replace(/{([^}]+)}/g, function(match, lookup) {
            return typeof args[lookup] != 'undefined'
                ? args[lookup]
                : match;
        });
    };

    var _visibleWithin = function($container, $elem) {
        return $container.innerHeight() > $elem.position().top;
    }

    var _fillWidth = function($elem) {
        var $parent = $elem.parent();
        var used = $elem.siblings().map(function() {
            return $(this).outerWidth(true);
        }).get().reduce(function(a, b) {
            return a + b;
        }, 0);
        var width = $parent.innerWidth() - used;
        $elem.outerWidth(width);
        return width;
    };

    var _setCaretPosition = function($input, index) {
        return $input.queue(function(next) {
            if (this.createTextRange) {
                var range = this.createTextRange();
                range.move("character", index);
                range.select();
            } else if (this.selectionStart !== null) {
                this.setSelectionRange(index, index);
            }
            next();
        });
    };

    var Terminal = function(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.init();
    };

    Terminal.prototype = {

        init: function() {

            /* elements */
            this.$terminal = $(this.element);
            this.$output = this.$terminal.find('.output');
            this.$input = this.$terminal.find('.input');
            this.$prompt = this.$input.find('.prompt');
            this.$cmdline = this.$input.find('input[type="text"]');

            this._prompt = this.options.prompt;
            this._term = '';

            /* history */
            this.initReadline();

            /* events */
            this.initEvents();

            return this;
        },

        initReadline: function() {

            this._history = this.options.history || new Josh.History({
                key: this.options.historyKey,
                unique: true
            });

            this._readline = this.options.readline || new Josh.ReadLine({
                element: this.$cmdline[0],
                history: this._history
            })

            /* readline events */
            this._readline.onEnter($.proxy(this.submit, this));
            this._readline.onCancel($.proxy(this.cancel, this));
            this._readline.onChange($.proxy(this.change, this));
            this._readline.onSearchStart($.proxy(this.searchStart, this));
            this._readline.onSearchChange($.proxy(this.searchChange, this));
            this._readline.onSearchEnd($.proxy(this.searchEnd, this));
        },

        initEvents: function() {
            var that = this;

            /* redraw when window resizes */
            $(window).resize($.proxy(this.redraw, this)).resize();

            /* focus cursor in a slightly clever manner */
            this.$terminal.mouseup(function(e) {
                switch (e.which) {
                    case 1:
                        if (_visibleWithin(that.$terminal, that.$cmdline) && window.getSelection() == "")
                            that.focus();
                        break;
                    default:
                        that.focus();
                        break;
                }
                return true;
            });

            this.$terminal.keypress(function() {
                that.focus();
                return true;
            });

        },

        submit: function(command, callback) {
            this.options.execute && this.options.execute(command);
            callback('');
        },

        change: function(line, changed) {
            if (!changed)
                return;
            this.$cmdline.val(line.text);
            _setCaretPosition(this.$cmdline, line.cursor);
        },

        cancel: function() {
            this._readline.setLine('', 0);
        },

        searchStart: function() {
            this.prompt(this.options.reverseSearchPrompt);
        },

        searchChange: function(match) {
            var term = match.term || '';
            if (match.text !== undefined)
                this.$cmdline.val(match.text);
            if (this._term != term) { 
                this._term = term;
                this.redraw();
            }
        },

        searchEnd: function() {
            this.prompt(this.options.prompt);
        },

        redraw: function() {
            this.$prompt.text(_format(this.prompt(), {term: this._term}));
            _fillWidth(this.$cmdline);
            return true;
        },

        focus: function() {
            this.$cmdline.focus();
        },

        hasFocus: function() {
            return this.$cmdline.is(':focus');
        },

        blur: function() {
            this.$cmdline.blur();
        },

        refocus: function(strict) {
            if (strict && !this.hasFocus())
                return;
            this.blur();
            this.focus();
        },

        history: function() {
            return this._history;
        },

        prompt: function(obj) {
            if (obj !== undefined) {
                this._prompt = obj;
                this.redraw();
            }
            if ($.isFunction(this._prompt))
                return this._prompt();
            return this._prompt;
        },

        command: function(obj) {
            var $elem, exists = false;
            if (obj.id) {
                $elem = $("#" + obj.id);
                exists = $elem.length > 0;
                if (!exists)
                    $elem = template.clone().attr('id', obj.id);
            } else {
                $elem = template.clone();
            }
            if (obj.request) {
                $elem.find('.request>.prompt').text(obj.request.prompt || this.prompt());
                $elem.find('.request>.cmdline').text(obj.request.cmdline);
            }
            if (obj.response) {
                $elem.find('.response').text(obj.response);
            }
            if (!exists)
                $elem.appendTo(this.$output);
        }

    };

    $.fn[pluginName] = function(options) {
        var terminals = this.map(function() {
            return new Terminal(this, options);
        });
        if (terminals.length == 1)
            return terminals[0];
        return terminals;
    };

})(jQuery, window, document);
