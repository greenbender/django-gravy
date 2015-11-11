;(function($, window, document, undefined) {

    var pluginName = 'simpleWebSocket',
        defaults = {
            basePath: '/ws',
            namespace: '',
            reconnect: true,
            reconnectTimeout: 500,
            autoConnect: true
        };

    /* helpers */
    var wsUri = function(options) {
        var uri = document.createElement('a');
        uri.href = window.location.href;
        uri.protocol = (uri.protocol == 'https:') ? 'wss:' : 'ws:';
        uri.pathname = options.basePath + '/' + options.namespace;
        uri.search = uri.hash = '';
        return uri.href;
    }

    var SimpleWebSocket = function(element, options) {
        this.element = element;
        this.options = $.extend({}, defaults, options, $(element).data());
        this.init();
    };

    SimpleWebSocket.prototype = {

        init: function() {
            this.$element = $(this.element);
            this.uri = wsUri(this.options);
            if (this.options.autoConnect)
                this.connect();
            return this;
        },

        connect: function() {
            if (this.socket !== undefined)
                return;
            if (this.options.reconnect)
                this.reconnect = true;
            this.socket = new WebSocket(this.uri);
            this.socket.onopen = $.proxy(this.onOpen, this);
            this.socket.onclose = $.proxy(this.onClose, this);
            this.socket.onerror = $.proxy(this.onError, this);
            this.socket.onmessage = $.proxy(this.onMessage, this);
        },

        disconnect: function() {
            if (this.socket === undefined)
                return;
            this.reconnect = false;
            this.socket.close();
        },

        send: function(event, data) {
            var pkt = JSON.stringify({
                'event': event,
                'data': data,
            });
            this.socket.send(pkt);
        },

        onOpen: function(event) {
            if (this.options.room)
                this.send('join', this.options.room);
        },

        onClose: function(event) {
            delete this.socket;
            if (this.reconnect)
                setTimeout($.proxy(this.connect, this), this.options.reconnectTimeout);
        },

        onError: function(event) {
            delete this.socket;
            if (this.reconnect)
                setTimeout($.proxy(this.connect, this), this.options.reconnectTimeout);
        },

        onMessage: function(event) {
            var that = this;
            var pkt = event.data;
            var data = JSON.parse(pkt);
            if (data.event == 'update') {
                $.each(data.data, function(name, value) {
                    var evt = $.Event('ws.update', {'value': value});
                    that.$element.find('[data-ws-name="' + name + '"]').each(function() {
                        var e = $(this);
                        if (e.data('wsUpdate') && e.html() != value)
                            e.html(value);
                        e.trigger(evt);
                    });
                });
            }
        }

    };

    $.fn[pluginName] = function(options) {
        return this.each(function() {
            if (!$.data(this, pluginName)) {
                $.data(this, pluginName, new SimpleWebSocket(this, options));
            }
        });
    };

    $('[data-toggle="' + pluginName + '"]')[pluginName]();

})(jQuery, window, document);
