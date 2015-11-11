(function($) {

    var getParent = function(elem) {
        var name = elem.data("parent");
        if (!name) return;
        var cascade = elem.closest("[data-toggle='selectCascade']");
        return cascade.find("select[name='" + name + "']").first();
    };

    var getParams = function(elem, params) {
        if (!elem) return params;
        var parent = getParent(elem);
        if (typeof params === "undefined")
            return getParams(parent, {});
        params[elem.attr("name")] = elem.val();
        return getParams(parent, params);
    };

    var setOptions = function(elem, options) {
        var current = elem.val();
        var hasCurrent = false;
        elem.empty();
        $.each(options, function(i, option) {
            elem.append($("<option>", {html:option.name, value:option.value}));
            if (option.value == current)
                hasCurrent = true;
        });
        if (hasCurrent)
            elem.val(current);
        elem.change();
    };

    $.fn.extend({

        selectCascade: function() {
            this.each(function() {
                var url = $(this).data("url");
                $(this).find("select[data-parent]").each(function() {
                    var elem = $(this);
                    getParent(elem).change(function() {
                        var params = getParams(elem);
                        $.get(url + '?' + $.param(params), function(data) {
                            setOptions(elem, data.options);
                        });
                    });
                });
            });
            return this;
        }

    });

    $('[data-toggle="selectCascade"]').selectCascade();

})(jQuery);

