Apros.models.ParticipantsAnalyticsChart = Apros.models.ServerModel.extend({

  setUrl: function(client_id, course_id){
    this.url = '/admin/client-admin/'+client_id+'/courses/'+course_id+'/analytics/participant';
  },

  parse: function(response) {

    return [
      {
        'bar': true,
        'color': '#3384CA',
        'key': '# Completed modules',
        'values': response.modules_completed
      },
      {
        'color': '#E37222',
        'key': '# of Participants',
        'values': response.participants
      }
    ]
  }

});
