Apros.views.AdminCourseMeta = Backbone.View.extend({
  events: {
    'change input': 'saveFeature'
  },

  saveFeature: function(e) {
    var form = $('#feature-flags-form');
    $.post(form.attr('action'), form.serialize())
  }
});
