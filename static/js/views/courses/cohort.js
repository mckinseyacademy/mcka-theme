Apros.views.CourseCohort = Backbone.View.extend({

  events: {
    'click .select-board a': 'update_scope'
  },

  update_scope: function(e) {
    e.preventDefault();
    var el = $(e.currentTarget).addClass('selected');
    this.$('.select-board a').not(el).removeClass('selected');
  },

  createIcon: function(user, loc, layers, x, y){
    var myIcon = L.icon({
      iconUrl: user.avatar_url,
      iconRetinaUrl: user.avatar_url,
      iconSize: [40, 40]
    });
    var marker = L.marker([(loc.lat + x), (loc.lon + y)], {icon: myIcon})
    .bindPopup('<h4>' + user.username + '</h4><p>Title: ' + user.title + '</p>');
    this.hoverizePopup(marker);
    layers.push(marker);
    return layers;
  },

  createCircle: function(data, city, layers){
      var city_name = data.query.join(' ');
      var radius = (50 * city.count) / (25 + city.count);
      var loc = data.results[0][0];

      var marker = L.circleMarker([loc.lat, loc.lon]).setRadius(radius)
        .bindPopup('<h4>' + city.name + '</h4><p>Participants: ' + city.count + '</p>');
      this.hoverizePopup(marker);
      layers.push(marker);
      return layers;
  },

  hoverizePopup: function(marker){
    marker.on('mouseover', function (e) {
      this.openPopup();
    });
    marker.on('mouseout', function (e) {
      this.closePopup();
    });
  },

  setCities: function(citiesMap, users, city_list, cities){
    $.each(citiesMap, function(key, value){
      var city = value.city.toLowerCase();
        city_list.push(city);
        cities[city] = ({'count': value.count, 'name': value.city, 'users': []});
    });
    $.each(users, function(key, value){
      var city = value.city.toLowerCase();
      if($.inArray(city, city_list) < 0){
        city_list.push(city);
        cities[city].name = value.city;
      }
      cities[city].users.push(value);
    });
  },

  render_map: function() {
    var _this = this;
    var users = CohortMapUsers;
    var citiesMap = CohortMapCities;
    var city_list = [];
    var layers = [];
    var cities = {};

    _this.setCities(citiesMap, users, city_list, cities);

    this.map = L.map('map-cohort', {zoomControl: true, attributionControl: false}).setView([51.505, -0.09], 1);
    L.tileLayer('https://{s}.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/{z}/{x}/{y}.png',{
      maxZoom: 18
    }).addTo(this.map);
    $.getJSON('https://api.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/geocode/' + city_list.join(';') + '.json').done(function(data){
      if(city_list.length == 1){
        var loc = data.results[0][0];
        layers = _this.createIcon(user, loc, layers, x, y);
        layers = _this.createCircle(data, cities[0], layers);
      }
      else if (city_list.length > 1){
        $.each(city_list, function(key, citykey){
          var city = cities[citykey]
          var numElements = city.users.length;
          var angle = 0;
          var step = (2*Math.PI) / numElements;
          layers = _this.createCircle(data[key], city, layers);
          $.each(city.users, function(key2, user){
            var x = 20 * Math.cos(angle);
            var y = 20 * Math.sin(angle);
            var loc = data[key].results[0][0];
            layers = _this.createIcon(user, loc, layers, x, y);
            angle += step;
          });
        });
      }
      L.layerGroup(layers).addTo(_this.map);
    })
  },

  render: function() {
    this.render_map();
  }
});
