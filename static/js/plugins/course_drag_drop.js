    $.courseDrag = function(){
      var course_id = $('#course_id').val();
      var data_table = $('.student-list').dataTable({
          paging: false
        });

      var accordianSlide = function(that, selected){
          if(selected.hasClass('expanded')){
              selected.removeClass('expanded').slideUp();
          }
          else{
              selected.addClass('expanded').slideDown();
          }
          that.find('i.caret').toggleClass('fa-caret-down').toggleClass('fa-caret-up');
        };

      var accordion = function(el, selector){
        el.find('.name').on('click', function(){
          var that = $(this);
          var selected = that.parent().find(selector);
          accordianSlide(that, selected);
        });
      };

      var removeStudent = function(el, link){
          var parent = el.parents('.select-group-box');
          data = {
            'student' : el.attr('name'),
            'csrfmiddlewaretoken':  $.cookie('apros_csrftoken'),
            'course_id': course_id
            };
          $.ajax(
          {
            url: link,
            data: data,
            method: 'POST'
          }).done(function(data){
            if(data != ''){
              data_table.fnDestroy();
              $('#student-list table').html(data);
              data_table= $('.student-list').dataTable({
                paging: false
              });
              $('.student[name="' + el.attr('name') + '"]').fadeOut().remove();
              parent.find('span.student-count').html(parent.find('span.student-count').html() - 1);
              enable_selection(selections, activator);
            }
          }).fail();
      };

      var updateGroup = function(group_id, students, url){
        $.ajax({
          url: url,
          data: {
            students: students,
            group_id: group_id,
            'csrfmiddlewaretoken':  $.cookie('apros_csrftoken'),
          },
          method: 'POST'
        }).done(function(data){
          if(data.status == 'success'){
            alert('Group successfully updated');
            window.location.hash = group_id;
            window.location.reload(true);
          }
          else {
            alert(data.status);
          }
        });
      };

      return {
        updateGroup: updateGroup,
        removeStudent: removeStudent,
        accordion: accordion,
        accordianSlide: accordianSlide,
        selections: selections,
        activator: activator,
        course_id: course_id,
        data_table: data_table
      }
    }

  $(function(){

    var course_id = $('#course_id').val();

    selections = [
      {
        selector: ".student-list .student",
        submit_name: "students",
        data_field: 'company-name',
        minimum_count_message: "Please select at least one student"
      }
    ];

    activator = {
      selector: '#student-group-action:not(.disabled)',
      success: function(){
        $('#student-group-action').removeClass('disabled');
        window.location = '/admin/workgroup/course/' + course_id;
      }
    };
  });

// UI EVENTS STUFF

  $(document).ready(function(){

    var courseDrag = $.courseDrag();

    // Preopening latest opened group
    if(window.location.hash != ''){
      var group = window.location.hash.split('#')[1];
      var that = $('#' + group);
      var selected = that.find('.group-info.students');
      courseDrag.accordianSlide(that, selected);
      window.location.hash = '';
    }

    enable_selection(selections, activator);

    courseDrag.accordion($('.select-group-box'), '.group-info.students');

    $('.remove-student-icon').on('click', function(e){
        e.preventDefault();
        courseDrag.removeStudent($(this), $(this).parent('a').attr('href'));
    });

    $('#student-group-action').on('click', function(){
      if(!$(this).hasClass('disabled')){
        $(this).addClass('disabled');
      }
    });

    $('.update-group').on('click', function(){
      var that = $(this);
      if(!that.hasClass('disabled')){
        var group = that.data('group-id');
        var privacy = that.data('privacy');
        var client_id = that.data('client-id');
        var url = that.data('url');
        var students = [];
        var allStudents = [];
        $('#student-list tr.student.selected').each(
          function(){
            if($(this).data('company-name') == client_id){
              students.push($(this).attr('id'));
            }
            allStudents.push($(this).attr('id'));
          });
        if(students.length == allStudents.length || privacy != 'private'){
          $('.update-group').addClass('disabled');
          courseDrag.updateGroup(group, allStudents, url);
        }
        else{
          alert('All students added to private group have to be members of same company.');
        }
      }
    });

    $('li.company-filter').on('click', function(){
      var that = $(this);
      if(that.data('company-filter') == 'all'){
        $('.select-group-box').show();
      }
      else{
        $('.select-group-box').hide();
        $('.select-group-box[data-client-id="' + that.data('company-filter') + '"]').show();
      }
    });

  });
