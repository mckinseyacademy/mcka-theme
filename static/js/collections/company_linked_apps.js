  Apros.collections.CompanyLinkedApps = Backbone.Collection.extend({
    initialize: function(options){
      this.url = options.url;
    },
    model: Apros.models.CompanyLinkedApps,
    parse: function(data){
      company_linked_apps = data['results'];
      return company_linked_apps;
    }
  });
