Apros.views.CourseCohort = Backbone.View.extend({

  render_map: function() {
    var _this = this;
    this.map = L.map('map-cohort', {zoomControl: true, attributionControl: false}).setView([51.505, -0.09], 1);
    L.tileLayer('https://{s}.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/{z}/{x}/{y}.png',{
      maxZoom: 18
    }).addTo(this.map);
    $.getJSON('http://api.tiles.mapbox.com/v3/mckinseyacademy.i2hg775e/geocode/london;new%20york%20city;san%20francisco.json').done(function(data){
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
