var map_opts = {
  zoomControl: true,
  minZoom: 1,
  zoom: 1,
  attributionControl: false,
  worldCopyJump: true
}

Apros.views.CourseCohort = Backbone.View.extend({

  iconsFlag: true,
  users: [],
  ta_user: [],
  city_list: [],
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

  initialize: function() {
    this.collection = new Apros.collections.CohortCities;
    this.listenTo(this.collection, 'sync', this.addGeodata);
    this.map = L.mapbox.map('map-cohort', mapbox_map_id, map_opts)
      .setView([51.505, -0.09], 1);
  },

  addGeodata: function(models) {
    var _this = this;
    var geoJsonData = {
      type: 'FeatureCollection',
      features: []
    }

    models.each(function(model){
      var size = model.size(),
          radius = 3 + (47 * size) / (25 + size);

      geoJsonData.features.push({
        type: 'Feature',
        properties: {
          count: radius,
          popup: '<div class="city-name">' + model.name() + '<div><div class="city-participants">Participants: ' + model.size() + '</div>'
        },
        geometry: {
          type: 'Point',
          coordinates: model.latLng()
        }
      });
    });

    var geoJson = L.geoJson(geoJsonData, {
      pointToLayer: function(feature, latlng) {
        var marker = L.circleMarker(latlng, {
          color: '#3384CA',
          fillColor: '#3384CA',
          stroke: false,
          fillOpacity: 0.5,
          radius: feature.properties.count
        });
        marker.bindPopup(feature.properties.popup, {'closeOnClick': false});
        _this.hoverizePopup(marker);
        return marker;
      }
    }).addTo(this.map);

  },

  update_scope: function(e) {
    e.preventDefault();
    var el = $(e.currentTarget).addClass('selected');
    this.$('.select-board a').not(el).removeClass('selected');
  },

  toggle_profiles: function(e) {
    e.preventDefault();
    this.$('.student-data a').toggle();
    var _this = this;
    this.iconsFlag = !this.iconsFlag;
    console.log(this.iconsFlag);
    this.map.featureLayer.setFilter(function(f){
      console.log(f.properties);
      return _this.iconsFlag;
    });
  },

  createIcon: function(user, loc, layers, x, y, className){
    var myIcon = L.icon({
      iconUrl: user.avatar_url,
      iconRetinaUrl: user.avatar_url,
      iconSize: [40, 40],
      className: className
    });
    if(user.title == null){
      user.title = '';
    }
    if(className == 'ta_user'){
      myIcon.iconSize = [44, 44];
      var marker = L.marker([(loc.lat + x), (loc.lon + y)], {icon: myIcon})
      .bindPopup('<div class="person-username">' + user.username + '</div><div class="person-fullname">' + user.full_name +
        '</div><div class="person-title">' + user.title + '</div><br><a href="#" data-reveal-id="contact-ta">Email</a>',
        {'closeOnClick': false});
    }else{
      var marker = L.marker([(loc.lat + x), (loc.lon + y)], {icon: myIcon})
      .bindPopup('<div class="person-username">' + user.username + '</div><div class="person-fullname">' + user.full_name +
        '</div><div class="person-title">' + user.title + '</div>',
        {'closeOnClick': false});
    }
    this.hoverizePopup(marker);
    layers.push(marker);
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

  render: function() {
    this.iconsFlag = true;
    this.collection.fetch();
  }
});
