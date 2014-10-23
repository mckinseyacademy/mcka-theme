Apros.models.CourseNote = Backbone.Model.extend({
  body: function() { return this.get('body'); },
  course_id: function() { return this.get('course_id'); },
  lesson_id: function() { return this.get('lesson_id'); }
});
