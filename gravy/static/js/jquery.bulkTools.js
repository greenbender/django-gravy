// TODO: properly jquerify this

$("[data-toggle='bulkSelector']").each(function() {
    var $this = $(this);
    var options = $this.data();
    $this.click(function() {
        $('input:checkbox[name="' + options.name + '"]').prop(
            'checked', $this.prop('checked')
        );
    });
});

$('a[data-toggle="bulkAction"]').each(function() {
    var $this = $(this);
    var options = $this.data();
    var base = $this.attr('href');
    var sep = (base.indexOf('?') > -1) ? '&' : '?';
    $this.click(function() {
        var params = [];
        $('input:checkbox[name="' + options.name + '"]:checked').each(function() {
            var $input = $(this);
            params.push({
                name: options.name,
                value: $input.val()
            });
        });
        if (params.length > 0)
            $this.attr('href', base + sep + $.param(params));
    });
});

$('form[data-toggle="bulkAction"]').each(function() {
    var $this = $(this);
    var options = $this.data();
    $this.submit(function() {
        var params = [];
        $('input:checkbox[name="' + options.name + '"]:checked').each(function() {
            $('<input>', {'type': 'hidden', 'name': options.name, 'value': $(this).val()}).appendTo($this);
        });
    });
});
