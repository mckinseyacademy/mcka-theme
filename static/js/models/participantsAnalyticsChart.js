Apros.models.ParticipantsAnalyticsChart = Apros.models.ServerModel.extend({

  setUrl: function(client_id, course_id){
    this.url = '/admin/client-admin/'+client_id+'/courses/'+course_id+'/analytics/participant';
  }

});
