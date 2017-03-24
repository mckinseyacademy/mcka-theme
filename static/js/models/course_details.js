  Apros.models.Course_Details = Backbone.Model.extend({
    parse: function (data, options) {
        options.parse = false; // Important: otherwise will produce endless recursion

        // creating a `dummy` record just to use `escape` functionality of backbone models
        var record = new this.collection.model(data, options);
        
        return Apros.utils.cleanParticipantProps(record, data);
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
