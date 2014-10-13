Apros.models.ServerModel = Backbone.Model.extend({

  sync: function(method, model, options) {
      var params = _.extend({
          type: 'GET',
          dataType: 'json',
          url: model.url,
          processData: false
      }, options);

      return $.ajax(params);
  }

});
