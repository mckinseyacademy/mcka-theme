$(function(){

  // Select courses
  $('.course-list .course').on('click', function(){
    $(this).toggleClass('selected');
  });

  $('#course-program-action').on('click', function(event){
    event.preventDefault();
    var program_course_ids = [];
    var selected_courses = $('.course-list .course.selected');

    if(selected_courses.length < 1){
      alert("Please select at least one course");
      return false;
    }

    program_course_ids = [];
    selected_courses.each(function(index, course){
      program_course_ids.push(course.id);
    });

    var use_url = $(this).attr('href');
    $.ajax({
      url: use_url,
      type: "POST",
      data: {
        "courses": program_course_ids,
        "csrfmiddlewaretoken": $.cookie('apros_csrftoken')
      },
      dataType: 'json',
      success: function(response){
        alert(response.message);
      }
    });

    return false;
  });

});