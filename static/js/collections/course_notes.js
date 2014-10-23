Apros.collections.CourseNotes = Backbone.Collection.extend({
  model: Apros.models.CourseNote,

  initialize: function(models, opts) {
    this.courseId = opts.courseId;
  },

  url: function() {
    return "/courses/" + this.courseId + "/notes/"
  }
});
