(function($) {

	var poll = function(url, interval, success) {
		$.ajax({
			url: url,
			dataType: 'html',
			success: success,
			complete: function() {
				if (interval) {
					setTimeout(function() {
						poll(url, interval, success);
					}, interval);
				}
			}
		});
	};

    $.fn.extend({

        ajaxUpdate: function() {

			this.each(function() {

				var elem = $(this);
				var url = elem.data('url');
				var interval = (elem.data('interval') || 0) * 1000;

				poll(url, interval, function(data) {
					if (elem.html() != data) {
						elem.html(data);
					}
				});

			});

			return this;

		}

	});

    $('[data-toggle="ajaxUpdate"]').ajaxUpdate();

})(jQuery);

