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
    'click .nav-right:not(.disabled)':  'rotate'
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

  render: function() {
    this.center_on_bookmark();

    var last_in_view = this.per_section - 1 >= this.cards.last().index();
    this.btn_right.toggleClass('disabled', last_in_view);
    var myNav = navigator.userAgent.toLowerCase();
    var browserVersion = (myNav.indexOf('msie') != -1) ? parseInt(myNav.split('msie')[1]) : false;
    if (browserVersion && browserVersion < 10){
      this.proficiencyIEfix();
    }
  },
  proficiencyIEfix: function(){
    var classes = $(".course-proficiency .visualization").attr('class').split(/\s+/);
    var percentage = 0;
    $.each(classes, function(index, item){
      if(item.indexOf('progress-') == 0){
        percentage = item.split('progress-')[1];
      }
    });
    var width = 100,
        height = 100,
        radius = Math.min(width, height) / 2;

    var color = d3.scale.ordinal()
        .range(["#333333", "#b1c2cc", "#7b6888"]);

    var arc = d3.svg.arc()
        .outerRadius(radius)
        .innerRadius(radius - 15);

    var pie = d3.layout.pie()
        .sort(null)
        .value(function(d) { return d.population; });

    $('.course-proficiency .progress-radial').remove();
    var svg = d3.select(".course-proficiency .visualization").append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var data=[{'population': percentage}, {'population': (100 - percentage)}];

    data.forEach(function(d) {
      d.population = +d.population;
    });

    var g = svg.selectAll(".arc")
        .data(pie(data))
      .enter().append("g")
        .attr("class", "arc");

    g.append("path")
        .attr("d", arc)
        .style("fill", function(d) { return color(d.value); });
  }
});
