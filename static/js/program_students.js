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

  $('#student-program-action').on('click', function(event){
    event.preventDefault();
    var program_student_ids = [];
    var selected_students = $('.student-list .student.selected');
    var selected_program = $('.program-selection .select-program-box.selected');

    if(selected_students.length < 1){
      alert("Please select at least one student");
      return false;
    }

    if(selected_program.length != 1){
      alert("Please select one program");
      return false;
    }

    var program_id = selected_program[0].id;
    selected_students.each(function(index, student){
      program_student_ids.push(student.id);
    });

    var use_url = $(this).attr('href');
    $.ajax({
      url: use_url,
      type: "POST",
      data: {
        "students": program_student_ids,
        "program": program_id,
        "csrfmiddlewaretoken": $.cookie('apros_csrftoken')
      },
      success: function(response){
        alert(response.message);
      }
    });

    return false;
  });

});
