Apros.collections.CohortCities = Backbone.Collection.extend({
  model: Apros.models.City,
  url: 'https://api.tiles.mapbox.com/v4/geocode/mapbox.places-v1/',

  city_url: function(cities) {
    var cityList = _(cities).reduce(function(list, city){
      var prefix = list.length ? ';' : '';
      return list += prefix + city.city;
    }, '');
    return this.url + cityList + '.json?access_token=' + mapbox_access_token;
  },

  fetch: function(opts) {
    var requests = [],
        _this = this,
        size = 50,
        dfd = new jQuery.Deferred();

    opts = opts ? _.clone(opts) : {};
    var method = opts.reset ? 'reset' : 'set';
    if (opts.parse === void 0) opts.parse = true;

    for (var i=0; i < CohortMapCities.length; i += size) {
        var cities = CohortMapCities.slice(i, i + size),
            url = _this.city_url(cities);
        requests.push($.get(url));
    }

    $.when.apply(undefined, requests)
      .pipe(function() {
        var args = Array.prototype.slice.call(arguments);
        if (_.isString(args[1])) {
          return args[0];
        }
        return $.map(arguments, function(item){return item[0]});
      })
      .done(function(resp) {
        _this[method](resp, opts);
        _this.trigger('sync', _this, resp, opts);
        dfd.resolve(resp);
      });

    return dfd.promise();
  },

  parse: function(response) {
    response = _(response).isArray() ? response : [response];
    var cities = _(response).map(function(city) {
      return _(city.features).find(function(feature) {
        return /^city|place/.test(feature.id);
      });
    });
    return _(cities).compact();
  }
});
