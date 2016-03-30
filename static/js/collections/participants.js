Apros.collections.Participants = Backbone.PageableCollection.extend({
  model: Apros.models.Participant,
  url: ApiUrls.participants_list,
  mode: "infinite",
  state: {
    firstPage:1,
    pageSize: 50
  },
  queryParams: {
    currentPage: "page",
    totalPages: null,
    totalRecords: null,
    has_organizations: true,
    page_size: 50,
  },
  parseLinks: function (resp, options) {
    returnObject={};
    if (resp['next'] != null){
      returnObject['next'] = ApiUrls.participants_list + '?'+resp['next'].split('?')[1];
    }
    if (resp['previous'] != null){
      returnObject['prev'] = ApiUrls.participants_list + '?'+resp['previous'].split('?')[1];
    }
    return returnObject;
  },
  parse: function(data) {
    participants = data.results;
    var items = [
      { 'name': 'organizations_custom_name', 'tag': 'company', 'value': participants[0]['organizations_custom_name']},
      { 'name': 'full_name', 'tag': 'name', 'value': participants[0]['full_name']},
      { 'name': 'email', 'tag': 'custom_email', 'value': participants[0]['email']}
    ];

    $.each(participants, function(i, user){
      $.each(items, function(j, item){
        if(item['value'] != user[item['name']]){
          items[j]['value'] = null
        }
      });
    });

    $.each(items, function(index, value){
      if(value['value']){
        highlightSearchBar(value);
      }
    });
      
    return participants;
  },
  updateQuerryParams: function(options){
    for (key in options)
      this.queryParams[key] = options[key];
    this.state['pageSize'] = 100;
    this.queryParams['page_size'] = 100;
  }
});