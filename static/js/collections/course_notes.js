Apros.collections.CourseNotes = Backbone.Collection.extend({
  model: Apros.models.CourseNote,

  initialize: function(models, opts) {
    this.courseId = opts.courseId;
    this.changeSort('lesson');
  },

  url: function() {
    return "/courses/" + this.courseId + "/notes/"
  },

  comparator: function (property) {
    return selectedStrategy.apply(myModel.get(property));
  },

  strategies: {
    lesson: function (note) { return (note.lesson_index() + 100) + note.module_index(); },
    time: function (note) { return new Date(note.created_at()).getTime(); }
  },

  changeSort: function (field) {
    this.comparator = this.strategies[field];
    this.sort();
  }
});
