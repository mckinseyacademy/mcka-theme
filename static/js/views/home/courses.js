Apros.views.HomeCourses = Backbone.View.extend({

  initialize: function() {
    this.rotator        = this.$('.rotator');
    this.slides         = $('.slides', this.rotator);
    this.cards          = $('li', this.slides);
    this.card_index     = 0;
    this.per_section    = Math.floor(this.rotator.width() / this.cards.width());
    this.btn_left       = $('.nav-left', this.rotator);
    this.btn_right      = $('.nav-right', this.rotator);

  },

  events: {
    'click .nav-left:not(.disabled)':   'rotate',
    'click .nav-right:not(.disabled)':  'rotate',
    'click .rotator a':                 'touchcheck',
    'touchstart .rotator':              'touchstart',
    'touchend .rotator':                'touchend'
  },

  rotate: function(event) {
    var el      = $(event.currentTarget);
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
    var last_in_view = el.index() + this.per_section -1 >= this.cards.last().index();
    this.card_index = this.cards.index(el);
    this.slides.css('margin-left', -el.position().left);
    this.btn_left.toggleClass('disabled', el.index() === 0);
    this.btn_right.toggleClass('disabled', last_in_view);
  },

  touchcheck: function(e) {
    if (this.current_touch) e.preventDefault();
  },

  touchstart: function(e) {
    this.current_touch = e.originalEvent.touches[0];
  },

  touchend: function(e) {
    _this = this;
    touch = e.originalEvent.changedTouches[0];
    diff  = this.current_touch.screenX - touch.screenX;
    console.log(diff);
    if (diff > 0) {
      this.$('.nav-right:not(.disabled)').click();
    } else {
      this.$('.nav-left:not(.disabled)').click();
    }

    setTimeout(function(){ delete _this.current_touch; }, 250);
  },

  render: function() {
    this.center_on_bookmark();

    var last_in_view = this.per_section - 1 >= this.cards.last().index();
    this.btn_right.toggleClass('disabled', last_in_view);
  }
});
