  Apros.models.Course_Details = Backbone.Model.extend({});

  Apros.models.CourseDetailsTimelineChart = Apros.models.ServerModel.extend({

  setUrl: function(course_id){
    this.url = '/admin/api/courses/'+course_id+'/timeline/';
  }

});
