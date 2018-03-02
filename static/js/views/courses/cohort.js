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
  map: null,
  initialize: function() {
     this.collection = new Apros.collections.CohortCities;
     this.listenTo(this.collection, 'sync', this.addGeodata);

    mapboxgl.accessToken = 'pk.eyJ1Ijoic2hhZnFhdGZhcmhhbiIsImEiOiJjamU1b2hoeXA0djVxMzNwZHg2MWdseXp0In0.xt99vVDUAFdmP_Lv2Eeamg';
    this.map = new mapboxgl.Map({
      container: 'map-cohort',
      style: 'mapbox://styles/mapbox/light-v9',
      center: [-0.09, 51.505],
      zoom: 1
    });

    mapboxgl.setRTLTextPlugin('https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.1.0/mapbox-gl-rtl-text.js');
    this.map.addControl(new MapboxLanguage({
       defaultLanguage: $('html').attr('lang')
    }));
  },
  geoJsonUserTemplate: function() {
    var geoJson = {
      type: 'FeatureCollection',
      features: []
    };
    return geoJson;
  },
  geoJsonCityTemplate: function () {
  var geoJson = {
        id: "cities",
        type: "circle",
        source: {
            type: "geojson",
            data: {
                type: "FeatureCollection",
                features: []
            }
        },
        paint: {
            'circle-color': '#3384CA',
            'circle-opacity': 0.5,
            'circle-radius': ['get', 'radius']
        }
      };
      return geoJson;
  },
  addGeodata: function(models) {
    var _this = this,
        cityJsonData = this.geoJsonCityTemplate(),
        userJsonData = this.geoJsonUserTemplate();

    models.each(function (model) {
        var users = model.users();
        cityJsonData.source.data.features.push(model.markerGeoJson());

        if (typeof TAUser !== 'undefined' && TAUser.username && model.name() === TAUser.city) {
            var user = model.userGeoJson(TAUser, users.length, true);
            userJsonData.features.push(user);
        }

        _(users).each(function (user, idx) {
            userJsonData.features.push(model.userGeoJson(user, idx));
        });
    });

    _this.map.on('load', function () {
        _this.map.addLayer(cityJsonData);

        userJsonData.features.forEach(function(marker) {
            var width = marker.properties.iconSize[0];
            var x_offset = -(marker.properties.iconAnchor[0] - (width/2));
            var y_offset = -(marker.properties.iconAnchor[1] - (width/2));
            var el = document.createElement('div');
            el.className = marker.properties.className;
            el.style.backgroundImage = marker.properties.iconUrl;
            el.style.width = marker.properties.iconSize[0] + 'px';
            el.style.height = marker.properties.iconSize[1] + 'px';
            var userPopup = new mapboxgl.Popup({
                closeOnClick: false,
                offset: [x_offset, y_offset]
            });
            el.addEventListener('mouseenter', function () {
                _this.map.getCanvas().style.cursor = 'pointer';
                userPopup.setLngLat(marker.geometry.coordinates)
                    .setHTML(marker.properties.popup)
                    .addTo(_this.map);
            });
            el.addEventListener('mouseleave', function () {
                _this.map.getCanvas().style.cursor = '';
                    setTimeout(function() {
                        userPopup.remove();
                    }, _this.popupTime);
            });

            new mapboxgl.Marker(el, {offset: [x_offset, y_offset]})
                .setLngLat(marker.geometry.coordinates)
                .addTo(_this.map);
        });

        var cityPopup = new mapboxgl.Popup({
            closeOnClick: false
        });

        function showPopup(e) {
            _this.map.getCanvas().style.cursor = 'pointer';
            cityPopup.setLngLat(e.features[0].geometry.coordinates)
              .setHTML(e.features[0].properties.popup)
              .addTo(_this.map);
        }

        function hidePopup() {
            _this.map.getCanvas().style.cursor = '';
            setTimeout(function() {
                cityPopup.remove();
            }, _this.popupTime);
        }

        _this.map.on('mouseenter', 'cities', showPopup);
        _this.map.on('mouseleave', 'cities', hidePopup);
    });
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

  render: function() {
    this.collection.fetch();
  }
});
