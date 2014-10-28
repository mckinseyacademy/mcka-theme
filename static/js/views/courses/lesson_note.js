var template_string = '<header>' +
                      '<span class="label-4"><%= lesson_name %> | </span>' +
                      '<span class="label-4 module"><%= module_name %> | </span>' +
                      '<time class="label-4" datetime="<%= created_at %>"><%= moment(created_at).format("M/D/YY h:mma") %></time>' +
                      '</header>' +
                      '<div class="body"><%= body %></div>';

Apros.views.LessonNote = Backbone.View.extend({
  tagName: "li",
  template: _.template(template_string),

  highlight: function(keyword) {
    var text = this.model.body();

    if (keyword.length) {
      var pattern = '\\b' + keyword;
      text = text.replace(new RegExp(pattern, 'gi'), '<span class="hlt">$&</span>');
    }

    this.$('.body').html(text);
  },

  render: function() {
    this.$el.html(this.template(this.model.attributes));
    return this;
  }
});
