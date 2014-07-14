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
    var city_list = [];
    $.each(users, function(key, value){
      city_list.push(value.city);
    });
    city_list = city_list.join(';');
    this.map = L.map('map-cohort', {zoomControl: true, attributionControl: false}).setView([51.505, -0.09], 1);
    L.tileLayer('https://{s}.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/{z}/{x}/{y}.png',{
      maxZoom: 18
    }).addTo(this.map);
    $.getJSON('https://api.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/geocode/' + city_list + '.json').done(function(data){
      for(var i=0, l=data.length; i<l; i++ ) {
        var loc = data[i].results[0][0];
        var radius = Math.floor(Math.random() * 10) + 5
        L.circleMarker([loc.lat, loc.lon]).setRadius(radius).addTo(_this.map);
      }
    })
  },

  render: function() {
    this.render_map();
  }
});
