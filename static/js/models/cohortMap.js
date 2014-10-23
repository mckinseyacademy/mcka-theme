Apros.models.LocationData = Backbone.Model.extend({

  sync: function(method, model, options) {
      var params = _.extend({
          type: 'GET',
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

  setUrl: function(query) {
    var query = (query == '') ? '%2F' : query,
        mb_token = $('meta[name=mapbox-token]').attr('content'),
        root_url = "https://api.tiles.mapbox.com/v4/geocode/mapbox.places-v1/";
    this.url = root_url + query + '.json?access_token=' + mb_token;
  }

});
