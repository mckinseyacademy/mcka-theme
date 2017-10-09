Apros.models.City = Backbone.Model.extend({

  name: function() { return this.get('text'); },
  latLng: function() { return this.get('geometry').coordinates; },

  size: function() {
    var name  = this.name().toLowerCase(),
        total = 0;
    var found = _(CohortMapCities).find(function(city){
      return city.city.toLowerCase() === name;
    });
    if (found) total = found.count;
    return total;
  },

  users: function() {
    var city = this.name();
    return _(CohortMapUsers).filter(function(user){
      return user.city === city;
    });
  },

  markerGeoJson: function() {
    var size = this.size(),
        radius = 3 + (47 * size) / (25 + size);

    var geoJson = {
      type: 'Feature',
      properties: {
        popup: '<div class="city-name">' + this.name() + '<div><div class="city-participants">Participants: ' + this.size() + '</div>',
        circle: {
          color: '#3384CA',
          fillColor: '#3384CA',
          stroke: false,
          fillOpacity: 0.5,
          radius: radius
        }
      },
      geometry: {
        type: 'Point',
        coordinates: this.latLng()
      }
    }

    return geoJson;
  },

  userGeoJson: function(user, idx, isTA) {
    var size = isTA ? 44 : 40;
    var className = isTA ? 'ta_user' : 'user';

    var geoJson = {
      type: 'Feature',
      properties: {
        popup: '<div class="person-username">' + user.username + '</div><div class="person-fullname">' + user.full_name + '</div><div class="person-title">' + user.title + '</div>',
        icon: {
          iconUrl: user.image_url_small,
          iconRetinaUrl: user.image_url_small,
          iconSize: [size, size],
          iconAnchor: [-8 * idx, (size / 2 * idx) + size],
          className: className
        }
      },
      geometry: {
        type: 'Point',
        coordinates: this.latLng()
      }
    }

    if (isTA) {
      geoJson.properties.popup += '<br><a href="#" data-reveal-id="contact-ta">Email</a>';
    }

    return geoJson;
  }
});
