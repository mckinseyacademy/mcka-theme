  Apros.collections.CompanyLearnerDashboards = Backbone.Collection.extend({
    initialize: function(options){
      this.url = options.url;
    },
    model: Apros.models.CompanyLearnerDashboards,
    parse: function(data){
      return data;
    }
  });