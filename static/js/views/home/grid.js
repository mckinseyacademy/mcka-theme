Apros.views.HomeGrid = Backbone.View.extend({

  scroll_window: function() {
    var $window     = $(window),
        w_width     = $window.width(),
        w_height    = $window.height(),
        tagline     = this.$('.tagline'),
        t_width     = tagline.width(),
        t_height    = tagline.height(),
        t_offset    = tagline.offset();

    $window
      .scrollTop(t_offset.top + (t_height / 2) - (w_height / 2))
      .scrollLeft(t_offset.left + (t_width / 2) - (w_width / 2));
  },

  render: function() {
    setTimeout(this.scroll_window, 10);
  }
});
