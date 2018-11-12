Apros.collections.companyCustomFieldsCollection = Backbone.Collection.extend({
    initialize: function(options){
      this.url = options.url;
    },
    parse: function(data){
      $('i.fa-spinner').hide();
      return data;
    }
  });
