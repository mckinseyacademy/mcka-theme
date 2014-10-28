Apros.models.CourseNote = Backbone.Model.extend({
  body: function() { return this.get('body'); },
  created_at: function() { return this.get('created_at'); },
  course_id: function() { return this.get('course_id'); },
  course_name: function() { return this.get('course_name'); },
  lesson_id: function() { return this.get('lesson_id'); },
  lesson_index: function() { return this.get('lesson_index'); },
  lesson_name: function() { return this.get('lesson_name'); },
  module_id: function() { return this.get('module_id'); },
  module_index: function() { return this.get('module_index'); },
  module_name: function() { return this.get('module_name'); }
});
