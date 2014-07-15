Apros.views.CourseCohort = Backbone.View.extend({

  events: {
    'click .select-board a': 'update_scope'
  },

  update_scope: function(e) {
    e.preventDefault();
    var el = $(e.currentTarget).addClass('selected');
    this.$('.select-board a').not(el).removeClass('selected');
  },

  render_map: function() {
    var _this = this;
    var users = CohortMapUsers;
    var citiesMap = CohortMapCities;
    var city_list = [];
    var cities = new Object();

    var createCircle = function(data, city, layers){
        var city_name = data.query.join(' ');
        var weight = city.count / 10;
        var loc = data.results[0][0];
        var radius = 20 * weight;

        var marker = L.circleMarker([loc.lat, loc.lon]).setRadius(radius)
          .bindPopup('<h4>' + city.city + '</h4><p>Participants: ' + city.count + '</p>');
        marker.on('mouseover', function (e) {
            this.openPopup();
        });
        marker.on('mouseout', function (e) {
            this.closePopup();
        });
        layers.push(marker);
        return layers;
    };

    var createIcon = function(user, loc, layers, x, y){
      var myIcon = L.icon({
          iconUrl: user.avatar_url,
          iconRetinaUrl: user.avatar_url,
          iconSize: [40, 40]
      });
      var marker = L.marker([(loc.lat + x), (loc.lon + y)], {icon: myIcon})
      .bindPopup('<h4>' + user.full_name + '</h4><p>Title: ' + user.title + '</p>');
        marker.on('mouseover', function (e) {
            this.openPopup();
        });
        marker.on('mouseout', function (e) {
            this.closePopup();
        });
      layers.push(marker);
      return layers;
    };

    $.each(users, function(key, value){
      var city = value.city.toLowerCase();
      if($.inArray(city, city_list) < 0){
        city_list.push(city);
        cities[city] = ({'weight': 1, 'name': value.city, 'users': [value]});
      }
      else{
        cities[city].weight += 0.5;
        cities[city].users.push(value);
      }
    });
    var citiesMapList = [];
    $.each(citiesMap, function(key, value){
      citiesMapList.push(value.city);
    });

    this.map = L.map('map-cohort', {zoomControl: true, attributionControl: false}).setView([51.505, -0.09], 1);
    L.tileLayer('https://{s}.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/{z}/{x}/{y}.png',{
      maxZoom: 18
    }).addTo(this.map);
    var layers = [];
    $.getJSON('https://api.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/geocode/' + city_list.join(';') + '.json').done(function(data){
      if(city_list.length == 1){
        var loc = data.results[0][0];
        layers = createIcon(user, loc, layers, x, y);
      }
      else if (city_list.length > 1){
        $.each(city_list, function(key, citykey){
          var city = cities[citykey]
          var numElements = city.users.length;
          var angle = 0;
          var step = (2*Math.PI) / numElements;
          $.each(city.users, function(key2, user){
            var x = 20 * Math.cos(angle);
            var y = 20 * Math.sin(angle);
            var loc = data[key].results[0][0];
            layers = createIcon(user, loc, layers, x, y);
            angle += step;
          });
        });
      }
      L.layerGroup(layers).addTo(_this.map);
    })
    $.getJSON('https://api.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/geocode/' + citiesMapList.join(';') + '.json').done(function(data){
      if(citiesMapList.length == 1){
        layers = createCircle(data, citiesMap[0], layers);
      }
      else if(citiesMapList.length > 1){
        for(var i=0, l=(data.length-1); i<=l; i++ ) {
          layers = createCircle(data[i], citiesMap[i], layers);
        }
      }
      L.layerGroup(layers).addTo(_this.map);
    })
  },

  render: function() {
    this.render_map();
  }
});
