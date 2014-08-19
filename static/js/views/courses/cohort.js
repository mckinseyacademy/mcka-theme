Apros.views.CourseCohort = Backbone.View.extend({

  profiles: true,
  layers: [],
  iconsFlag: true,
  fetchedData: false,
  userProfilesVisible: true,
  users: [],
  ta_user: [],
  citiesMap: [],
  city_list: [],
  cities: {},
  zoomLevel: 1,
  popupTimeout: false,
  popupTime: 700,

  defaults: {
    model: new Apros.models.LocationData
  },

  events: {
    'click .select-board a': 'update_scope',
    'click .student-data a': 'toggle_profiles'
  },

  initialize: function(){
    var _this = this;
    var tile_url = 'https://{s}.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/{z}/{x}/{y}.png';
    var map_opts = {
      zoomControl: true,
      minZoom: 1,
      zoom: 1,
      center: [51.505, -0.09],
      attributionControl: false
    }

    this.users = CohortMapUsers;
    this.ta_user = TAUser;
    this.citiesMap = CohortMapCities;
    this.setCities(this.citiesMap, this.users, this.ta_user, this.city_list, this.cities);
    this.model.setUrl(this.city_list.join(';'));
    this.map = L.map('map-cohort', map_opts);
    L.tileLayer(tile_url).addTo(this.map);
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
    this.delayPopupClose();
    if(this.city_list.length > 0){
      this.model.fetch({
        'success': function(model, response){
          model.save(model.parse(response));
          _this.render();
        }
      });
    }
  },

  update_scope: function(e) {
    e.preventDefault();
    var el = $(e.currentTarget).addClass('selected');
    this.$('.select-board a').not(el).removeClass('selected');
  },

  toggle_profiles: function(e) {
    var _this = this;
    e.preventDefault();
    this.map.removeLayer(_this.layers);
    this.iconsFlag = !this.iconsFlag;
    $('.student-data a').toggle();
    this.render_map();
  },

  createIcon: function(user, loc, layers, x, y, className){
    var myIcon = L.icon({
      iconUrl: user.avatar_url,
      iconRetinaUrl: user.avatar_url,
      iconSize: [40, 40],
      className: className
    });
    if(user.title == null){
      user.title = 'N/A';
    }
    if(className == 'ta_user'){
      myIcon.iconSize = [44, 44];
      var marker = L.marker([(loc.lat + x), (loc.lon + y)], {icon: myIcon})
      .bindPopup('<div class="person-name">' + user.username + '</div><div class="person-fullname">' + user.full_name + 
        '</div><div class="person-title">Teaching Assistent</div><br><a href="#" data-reveal-id="contact-ta">Email Group TA</a>',
        {'closeOnClick': false});
    }else{
      var marker = L.marker([(loc.lat + x), (loc.lon + y)], {icon: myIcon})
      .bindPopup('<div class="person-name">' + user.username + '</div><div class="person-fullname">' + user.full_name + 
        '</div><div class="person-title">' + user.title + '</div>',
        {'closeOnClick': false});
    }
    this.hoverizePopup(marker);
    layers.push(marker);
    return layers;
  },

  createCircle: function(data, city, layers){
      var city_name = data.query.join(' ');
      var radius = 3 + (47 * city.count) / (25 + city.count);
      if(typeof data.results[0] != 'undefined'){
        var loc = data.results[0][0];
        var marker = L.circleMarker([loc.lat, loc.lon], {
            color: '#3384CA',
            fillColor: '#3384CA',
            stroke: false,
            fillOpacity: 0.5
        }).setRadius(radius)
          .bindPopup('<div class="city-name">' + city.name + '<div><div class="city-participants">Participants: ' + city.count + '</div>',
            {'closeOnClick': false});
        this.hoverizePopup(marker);
        layers.push(marker);
      }
      return layers;
  },

  hoverizePopup: function(marker){
    var _this = this;
    marker.on('mouseover', function (e) {
      this.openPopup();
    });
    marker.on('mouseout', function (e) {
      var that = this;
      _this.popupTimeout = setTimeout(function(){that.closePopup();}, _this.popupTime);
    });
  },

  delayPopupClose: function(){
    var _this = this;
    var popup = $('.leaflet-popup-pane');
    popup.on('mouseover', function(){
      clearTimeout(_this.popupTimeout);
    });
    popup.on('mouseout', function (e) {
      var that = this;
      _this.popupTimeout = setTimeout(function(){_this.map.closePopup();}, _this.popupTime);
    });
  },

  setCities: function(citiesMap, users, ta_user, city_list, cities){
    $.each(citiesMap, function(key, value){
      if(value.city){
        var city = value.city.toLowerCase();
        city_list.push(city);
        cities[city] = ({'count': value.count, 'name': value.city, 'users': [], 'ta_user': []});
      }
    });
    $.each(users, function(key, value){
      if(value.city){
        var city = value.city.toLowerCase();
        if($.inArray(city, city_list) < 0){
          city_list.push(city);
          cities[city] = ({'name': value.city, 'users': [], 'ta_user': []});
        }
        cities[city].users.push(value);
      }
    });
    if(typeof ta_user.city != 'undefined'){
      var city = ta_user.city.toLowerCase();
      if($.inArray(city, city_list) < 0){
        city_list.push(city);
        cities[city] = ({'name': ta_user.city, 'ta_user': []});
      }
      cities[city].ta_user = ta_user;
    }
    this.cities = cities;
  },

  drawLayers: function(data, city_list, cities, users, iconsFlag){
      var layers = [];
      var _this = this;
      $.each(city_list, function(key, citykey){
        var city = cities[citykey];
        var numElements = 0;
        if(city && city.users){
          numElements = city.users.length + 1;
        }
        var angle = 0;
        var step = (2*Math.PI) / numElements;
        var cityData = data.get(citykey);
        if(typeof cityData != 'undefined'){
          if(typeof cityData.results != 'undefined'){
            if(typeof cityData.results[0] != 'undefined'){
              layers = _this.createCircle(cityData, city, layers);
              if(iconsFlag){
                var loc = cityData.results[0][0];
                if(city.users.length > 0){
                  $.each(city.users, function(key2, user){
                    if(typeof cityData.results[0] != 'undefined'){
                      layers = _this.drawUserIcon(user, layers, loc, angle, step, 'user');
                      angle += step;
                    }
                  });
                }
                if(typeof city.ta_user.username != 'undefined'){
                  layers = _this.drawUserIcon(city.ta_user, layers, loc, angle, step, 'ta_user');
                  angle += step;
                }
              }
            }
          }
        }
      });
      this.layers = L.layerGroup(layers).addTo(_this.map);
    },

  drawUserIcon: function(user, layers, loc, angle, step, className){
    var _this = this;
    var zoomFactor = Math.pow(2, (_this.zoomLevel - 1));
    var x = 20 / zoomFactor * Math.cos(angle);
    var y = 20 / zoomFactor * Math.sin(angle);
    layers = _this.createIcon(user, loc, layers, x, y, className);
    return layers;
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
