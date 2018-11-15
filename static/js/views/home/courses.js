Apros.views.HomeCourses = Backbone.View.extend({

  initialize: function() {
    this.rotator        = this.$('.rotator');
    this.slides         = $('.slides', this.rotator);
    this.cards          = $('li', this.slides);
    this.per_section    = Math.floor(this.rotator.width() / this.cards.width());
    this.btn_left       = $('.nav-left', this.rotator);
    this.btn_right      = $('.nav-right', this.rotator);
    this.direction      = $("html").attr("dir");
    if(this.direction == "rtl")
      this.card_index = this.cards.length - 1;
    else
      this.card_index = 0;
  },

  events: {
    'click .nav-left:not(.disabled)':   'rotate',
    'click .nav-right:not(.disabled)':  'rotate',
  },

  rotate: function(event) {
    var el = $(event.currentTarget);
    var offset  = el.is('.nav-left') ? -this.per_section : this.per_section;
    var idx     = this.card_index + offset;
    if (idx < 0) idx = 0;
    if (idx > this.cards.length -1) idx = this.cards.length - 1;
    this.slide_to(this.cards.eq(idx));
  },

  center_on_bookmark: function() {
    var _this     = this;
    var center    = Math.ceil(this.per_section / 2) - 1;
    var bookmark  = $('.bookmark', this.slider).parents('li');
    if (bookmark.length && bookmark.index() > center) {
      var el = this.cards.eq(bookmark.index() - center);
      this.slide_to(el);
    }
    _.delay(function() { _this.slides.addClass('animate'); }, 10);
  },

  slide_to: function(el) {
    this.card_index = this.cards.index(el);

    if(this.direction == "rtl") {
      var last_in_view = el.index() >= this.cards.last().index();
      this.slides.css('margin-right', -el.position().left);
      this.btn_left.toggleClass('disabled', el.index() <= this.per_section);
    }
    else{
      var last_in_view = el.index() + this.per_section - 1 >= this.cards.last().index();
      this.slides.css('margin-left', -el.position().left);
      this.btn_left.toggleClass('disabled', el.index() === 0);
    }
    this.btn_right.toggleClass('disabled', last_in_view);

  },

  render: function() {
    this.center_on_bookmark();

    var last_in_view = this.per_section - 1 >= this.cards.last().index();

    if(this.direction == "rtl")
      this.btn_left.toggleClass('disabled', last_in_view);
    else
      this.btn_right.toggleClass('disabled', last_in_view);

    _this = self;
    this.$(".rotator").touchwipe({
      wipeLeft: function() { _this.$('.nav-right:not(.disabled)').click(); },
      wipeRight: function() { _this.$('.nav-left:not(.disabled)').click(); },
      min_move_x: 20,
      min_move_y: 20,
      preventDefaultEvents: true
    });
  }
});
