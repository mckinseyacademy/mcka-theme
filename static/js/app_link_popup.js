$(function(){
    if($('#mobileAppLinkModal').length > 0){
        $('#mobileAppLinkModal').foundation('reveal', 'open');
    }

    function trackAppDownloadLinkClick(link, username, platform) {
        setTimeout(visitLink, 1000);

        var link_visited = false;

        function visitLink() {
            if (!link_visited) {
                link_visited = true;
                window.location.href = link;
            }
        }

        ga('send', 'event', 'Outbound Link', 'click', platform + ' App Download', {
            'username': username,
            hitCallback: visitLink
        });

    }
    $("#ios_download_link").on('click', function(event) {
        event.preventDefault();
        trackAppDownloadLinkClick(this.href, $(this).data('username'), 'iOS' )
    });
    $("#android_download_link").on('click', function(event) {
        event.preventDefault();
        trackAppDownloadLinkClick(this.href, $(this).data('username'), 'Android' )
    });

});

// Diable scrollbar on popup show

$(document).on('open', '#mobileAppLinkModal', function () {
    $('body').css("overflow", "hidden");
});
$(document).on('close', '#mobileAppLinkModal', function () {
    $('body').css("overflow", "auto");
});