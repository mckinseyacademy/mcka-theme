$(function(){

  // Select students
  $('.student-list .student').on('click', function(){
    $(this).toggleClass('selected');
  });

  // Select program
  $('.program-selection .select-program-box').on('click', function(){
    $('.program-selection .select-program-box').removeClass('selected');
    $(this).addClass('selected');
  });

  $('#student-course-action').on('click', function(event){
    event.preventDefault();
    var selected_students = $('.student-list .student.selected');
    var selected_courses = $('.program-selection .select-program-box.selected input[type=checkbox]:checked');

    if(selected_students.length < 1){
      alert("Please select at least one student");
      return false;
    }

    if(selected_courses.length < 1){
      alert("Please select one course");
      return false;
    }

    var program_student_ids = [];
    var program_course_ids = [];
    selected_students.each(function(index, student){
      program_student_ids.push(student.id);
    });
    selected_courses.each(function(index, course){
      program_course_ids.push(course.id);
    });

    var use_url = $(this).attr('href');
    $.ajax({
      url: use_url,
      type: "POST",
      data: {
        "students": program_student_ids,
        "courses": program_course_ids,
        "csrfmiddlewaretoken": $.cookie('apros_csrftoken')
      },
      success: function(response){
        alert(response.message);
      }
    });

    return false;
  });

});
