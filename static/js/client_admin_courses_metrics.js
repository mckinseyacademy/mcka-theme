$(function(){
  var courses_list = JSON.parse($('#courses_list').val());
  var arrays = [], size = 12;
  while (courses_list.length > 0)
      arrays.push(courses_list.splice(0, size));

  for (var i=0; i < arrays.length; i++) {

    function get_courses_tiles() {
      if (arrays.length > 0 ) {
        var optionsData = {'courses_list': arrays.splice(0, 1)[0]};
        var options = {
            url: window.location.href,
            data: optionsData,
            type: "POST",
          };
          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};

          $.ajax(options).done(function(data){ 
            $('ul.courses-tiles').append(data);
            get_courses_tiles();
          }).fail(function(error){
            arrays = [];
            get_courses_tiles();
          });
      }
    }
    get_courses_tiles();
  }
})
