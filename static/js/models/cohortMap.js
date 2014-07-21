Apros.models.LocationData = Backbone.Model.extend({

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
