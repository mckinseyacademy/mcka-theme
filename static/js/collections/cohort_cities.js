Apros.collections.CohortCities = Backbone.Collection.extend({
  model: Apros.models.City,

  url: function() {
    var cityList = _(this.userCities()).keys().join(';');
    return 'https://api.tiles.mapbox.com/v4/geocode/mapbox.places-v1/' + cityList + '.json?access_token=' + L.mapbox.accessToken;
  },

  parse: function(response) {
    var cities = _(response).map(function(city) {
      return _(city.features).find(function(feature) {
        return /^city/.test(feature.id);
      });
    });
    return _(cities).compact();
  },

  userCities: function() {
    if (this.citySize) return this.citySize;
    this.citySize = _(CohortMapUsers).countBy(function(user){
      return user.city;
    });
    return this.citySize;
  }
});
