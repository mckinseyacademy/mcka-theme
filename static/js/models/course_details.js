  Apros.models.Course_Details = Backbone.Model.extend({
    parse: function (data, options) {
        return Apros.utils.cleanParticipantProps(data);
    }
  });

  Apros.models.CourseDetailsTimelineChart = Apros.models.ServerModel.extend({

  setUrl: function(course_id){
    var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
    if (companyPageFlag == 'True')
    {
      var companyId = $('#courseDetailsDataWrapper').attr('company-id');
      this.url = '/admin/api/courses/'+course_id+'/timeline/?company_id=' + companyId;
    }
    else
    {
      this.url = '/admin/api/courses/'+course_id+'/timeline/';
    }
  }

});
