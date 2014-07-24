Apros.models.LocationData = Backbone.Model.extend({

  sync: function(method, model, options) {
      var params = _.extend({
          type: 'GET',
          dataType: 'jsonp',
          url: model.url,
          processData: false
      }, options);

      return $.ajax(params);
  },

  parse: function(data){
    if(typeof data.query != 'undefined'){
      data = [data];
    }
    var response = [];
    _.each(data, function(value, key){
      response[value.query.join(' ')] = value;
    });
    return response;
  },

  setUrl: function(query){
    this.url = 'https://api.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/geocode/' + query + '.json';
  }

});
