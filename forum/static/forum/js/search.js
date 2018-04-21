$('.searchBar').autocomplete({
	source:function(request, response) {
        $.ajax({
            url: "/roc2/search/search.php",
            type: "GET",
            dataType: "json",
            delay: 500,
            data: { term: request.term },
            success: function(data) {
                response($.map(data, function(item) {
                    return {
                        label: item.Title + " (" + item.Count+ ")",
                        value: item.Title,
                        id: item.Id,
                        title: item.Title
                    };
                }));
            }
        });
    },
    minLength:0,
    select: function(event,ui){ 
        window.location.href = "/roc2/search?search=" + ui.item.id;
    }
});

jQuery.ui.autocomplete.prototype._resizeMenu = function () {
  	var ul = this.menu.element;
  	//ul.outerWidth(this.element.outerWidth());
};

$('.searchBox').click(function() {
	console.log($(this).value());

    // TODO fix this
});