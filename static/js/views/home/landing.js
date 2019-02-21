Apros.views.HomeLanding = Backbone.View.extend({

    initialize: function () {
        _(this).bindAll('scroll_window');
        if ($('#generalModal input.show-modal').length > 0) {
            $('html,body').css('width', '100%');
            $('html,body').css({'margin': '0 auto 100px', 'width': '1800px'});
        }
    },

    scroll_window: function () {
        var $window = $(window),
            tagline = this.$('.tagline'),
            t_width = tagline.width(),
            t_offset = tagline.offset();

        var render_warning_popup = function () {
            if ($('#generalModal input.show-modal').length > 0) {
                setTimeout(function () {
                    $('#generalModal').foundation('reveal', 'open');
                }, 500);
            }
        }
        if (t_offset !== undefined) {
            $('html,body').animate({
                scrollTop: t_offset.top - ($window.height() - tagline.outerHeight(true)) / 2,
                scrollLeft: t_offset.left - ($window.width() - tagline.outerWidth(true)) / 2
            }, 0, render_warning_popup());
        }
    },

    render: function () {
        setTimeout(this.scroll_window, 10);
    }
});
