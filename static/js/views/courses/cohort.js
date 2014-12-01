var map_opts = {
  zoomControl: true,
  minZoom: 1,
  zoom: 1,
  attributionControl: false,
  worldCopyJump: true
}

Apros.views.CourseCohort = Backbone.View.extend({

  popupTime: 700,

  events: {
    'click .select-board a': 'update_scope',
    'click .student-data a': 'toggle_profiles'
  },

  initialize: function() {
    this.collection = new Apros.collections.CohortCities;
    this.listenTo(this.collection, 'sync', this.addGeodata);
    this.map = L.mapbox.map('map-cohort', mapbox_map_id, map_opts)
      .setView([51.505, -0.09], 1);
    this.mapLayer = L.mapbox.featureLayer().addTo(this.map);
    this.listenTo(this.mapLayer, 'layeradd', this.addLayer);
  },

  geoJsonTemplate: function() {
    var geoJson = {
      type: 'FeatureCollection',
      features: []
    }
    return geoJson;
  },

  addGeodata: function(models) {
    var _this = this,
        cityJsonData = this.geoJsonTemplate(),
        userJsonData = this.geoJsonTemplate();

    models.each(function(model){
      var users = model.users()
      cityJsonData.features.push(model.markerGeoJson());

      if (typeof TAUser !== 'undefined' && TAUser.username && model.name() === TAUser.city) {
        var user = model.userGeoJson(TAUser, users.length, true);
        userJsonData.features.push(user);
      }

      _(users).each(function(user, idx){
        userJsonData.features.push(model.userGeoJson(user, idx));
      });
    });

    var geoJson = L.geoJson(cityJsonData, {
      pointToLayer: function(feature, latlng) {
        var marker = L.circleMarker(latlng, feature.properties.circle);
        marker.bindPopup(feature.properties.popup, {'closeOnClick': false});
        _this.hoverizePopup(marker);
        return marker;
      }
    }).addTo(this.map);

    this.mapLayer.setGeoJSON(userJsonData);
  },

  addLayer: function(e) {
    var marker = e.layer,
        feature = marker.feature,
        width = feature.properties.icon.iconSize[0],
        offset = [0,0];

    if (feature.properties.icon) {
      marker.setIcon(L.icon(feature.properties.icon));
      offset[0] = -(feature.properties.icon.iconAnchor[0] - (width/2))
      offset[1] = -(feature.properties.icon.iconAnchor[1] - (width/2))
    }

    var popup_opts = {
      closeOnClick: false,
      offset: offset
    }

    marker.bindPopup(feature.properties.popup, popup_opts);
    this.hoverizePopup(marker);
  },

  update_scope: function(e) {
    e.preventDefault();
    var el = $(e.currentTarget).addClass('selected');
    this.$('.select-board a').not(el).removeClass('selected');
  },

  toggle_profiles: function(e) {
    e.preventDefault();
    var _this = this,
        el = $(e.currentTarget),
        show = /Show/.test(el.text());
    this.$('.student-data a').toggle();
    this.mapLayer.setFilter(function(f){
      var toggle = f.properties.icon ? show : true;
      return toggle;
    });
  },

  hoverizePopup: function(marker){
    var _this = this;
    marker.on('mouseover', function (e) {
      this.openPopup();
      clearTimeout(marker.timer);
    });
    marker.on('mouseout', function (e) {
      var that = this;
      marker.timer = setTimeout(function(){that.closePopup();}, _this.popupTime);
    });
  },

  render: function() {
    this.collection.fetch();
  }
});
