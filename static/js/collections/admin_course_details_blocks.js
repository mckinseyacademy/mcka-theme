Apros.collections.CourseDetailsBlocks = Backbone.Collection.extend({
  model: Apros.models.AdminCourseDetailsBlocks,
  url: function () {
    return ApiUrls.course_blocks();
  }
});
