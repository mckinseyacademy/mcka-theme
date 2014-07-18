Apros.views.CourseCohort = Backbone.View.extend({

  profiles: true,
  layers: [],
  iconsFlag: true,
  fetchedData: false,
  userProfilesVisible: true,
  users: [],
  citiesMap: [],
  city_list: [],
  cities: {},
  zoomLevel: 1,

  defaults: {
    model: new Apros.models.LocationData
  },

  events: {
    'click .select-board a': 'update_scope',
    'click .student-data a': 'toggle_profiles'
  },

  initialize: function(){
    var _this = this;
    this.users = CohortMapUsers;
    this.citiesMap = CohortMapCities;

    this.setCities(this.citiesMap, this.users, this.city_list, this.cities);
    this.model.setUrl(this.city_list.join(';'));
    this.map = L.map('map-cohort', {zoomControl: true, attributionControl: false}).setView([51.505, -0.09], 1);
    L.tileLayer('https://{s}.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/{z}/{x}/{y}.png',{
        maxZoom: 18
      }).addTo(this.map);
    this.map.on('zoomend', function(){
      if(_this.map.getZoom() >= 1){
        _this.zoomLevel = _this.map.getZoom();
      }
      else{
        _this.zoomLevel = 1;
      }
      _this.map.removeLayer(_this.layers);
      _this.drawLayers(_this.model, _this.city_list, _this.cities, _this.users, _this.iconsFlag);
    });
    this.model.fetch({
      'success': function(model, response){
        model.save(model.parse(response));
        _this.render();
      }
    });
  },

  update_scope: function(e) {
    e.preventDefault();
    var el = $(e.currentTarget).addClass('selected');
    this.$('.select-board a').not(el).removeClass('selected');
  },

  toggle_profiles: function(e) {
    e.preventDefault();
    this.map.removeLayer(_this.layers);
    this.iconsFlag = !this.iconsFlag;
    $('.student-data a').toggle();
    this.render_map();
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
      if(typeof data.results[0] == 'undefined'){
        var loc = data.results[0][0];
        var marker = L.circleMarker([loc.lat, loc.lon]).setRadius(radius)
          .bindPopup('<h4>' + city.name + '</h4><p>Participants: ' + city.count + '</p>');
        this.hoverizePopup(marker);
        layers.push(marker);
      }
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

  drawLayers: function(data, city_list, cities, users, iconsFlag){
      var layers = [];
      var _this = this;
      $.each(city_list, function(key, citykey){
        var city = cities[citykey]
        var numElements = city.users.length;
        var angle = 0;
        var step = (2*Math.PI) / numElements;
        layers = _this.createCircle(data.get(citykey), city, layers);
        if(iconsFlag){
          $.each(city.users, function(key2, user){
            var cityData = data.get(citykey);
            if(typeof cityData.results[0] != 'undefined'){
              var zoomFactor = Math.pow(2, (_this.zoomLevel - 1));
              var x = 20 / zoomFactor * Math.cos(angle);
              var y = 20 / zoomFactor * Math.sin(angle);
              var loc = cityData.results[0][0];
              layers = _this.createIcon(user, loc, layers, x, y);
              angle += step;
            }
          });
        }
      });
      this.layers = L.layerGroup(layers).addTo(_this.map);
    },

  render_map: function() {
    var _this = this;
    this.drawLayers(this.model, this.city_list, this.cities, this.users, this.iconsFlag);
  },

  render: function() {
    this.iconsFlag = true;
    this.render_map(true);
  }
});
