Apros.models.City = Backbone.Model.extend({

  name: function() { return this.get('text'); },
  latLng: function() { return this.get('geometry').coordinates; },

  size: function() {
    var city = this.get('text');
    return this.collection.userCities()[city];
  }
});
