Apros.views.HomeLanding = Backbone.View.extend({

  initialize: function() {
    _(this).bindAll('scroll_window');
  },

  scroll_window: function() {
    var $window     = $(window),
        w_width     = $window.width(),
        tagline     = this.$('.tagline'),
        t_width     = tagline.width(),
        t_offset    = tagline.offset();

    $('html,body').animate({
        scrollTop: t_offset.top - ($window.height() - tagline.outerHeight(true)) / 2,
        scrollLeft: t_offset.left - (this.$el.outerWidth(true) - tagline.outerWidth(true)) / 2
    }, 0);
  },

  render: function() {
    setTimeout(this.scroll_window, 10);
  }
});
