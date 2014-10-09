(function ($) {
  $.urlParam = function(name, url) {
      if (!url) {
       url = window.location.href;
      }
      var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(url);
      if (!results) {
          return 0;
      }
      return results[1] || 0;
  }
}(jQuery));
