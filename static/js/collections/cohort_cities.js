Apros.collections.CohortCities = Backbone.Collection.extend({
  model: Apros.models.City,

  url: function() {
    var cityList = _(CohortMapCities).reduce(function(list, city){
      var prefix = list.length ? ';' : '';
      return list += prefix + city.city;
    }, '');
    return 'https://api.tiles.mapbox.com/v4/geocode/mapbox.places-v1/' + cityList + '.json?access_token=' + L.mapbox.accessToken;
  },

  parse: function(response) {
    response = _(response).isArray() ? response : [response];
    var cities = _(response).map(function(city) {
      return _(city.features).find(function(feature) {
        return /^city|place/.test(feature.id);
      });
    });
    return _(cities).compact();
  }
});
