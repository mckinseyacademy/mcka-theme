(function() {
	$('.debug-roundtrip-more').on('click', function(e) {
        e.preventDefault();
        $(this).next().toggle();
        return false;
    });
})();
