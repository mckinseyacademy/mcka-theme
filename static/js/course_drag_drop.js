    $.courseDrag = function(){
      var course_id = $('#course_id').val();
      var data_table = $('.student-list').dataTable({
          paging: false,
          autoWidth: false,
          scrollX: true
        });

      var accordianSlide = function(that, selected){
          if (selected.hasClass('expanded')) {
              selected.removeClass('expanded').slideUp();
          } else {
              selected.addClass('expanded').slideDown();
          }
          that.find('i.caret').toggleClass('fa-caret-down').toggleClass('fa-caret-up');
        };

      var accordion = function(el, selector){
        el.find('.group-data').on('click', function(){
          var that = $(this);
          var selected = that.parent().find(selector);
          accordianSlide(that, selected);
        });
        el.find('.group-detail').on('click', function(ev){
          ev.stopPropagation();
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
                paging: false,
                autoWidth: false,
                scrollX: true
              });
              $('.student[name="' + el.attr('name') + '"]').fadeOut().remove();
              parent.find('span.student-count').html(parent.find('div.student').length);
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

      var list_groups_for_selected_project = function(project_id){
        var groupBoxes = $('.select-group-box').hide();
        groupBoxes.filter('[data-project-id="' + project_id + '"]').show();
      };

      return {
        updateGroup: updateGroup,
        removeStudent: removeStudent,
        accordion: accordion,
        accordianSlide: accordianSlide,
        selections: selections,
        activator: activator,
        course_id: course_id,
        data_table: data_table,
        list_groups_for_selected_project: list_groups_for_selected_project
      }
    }

  $(function(){

    var course_id = $('#course_id').val();

    selections = [
      {
        selector: ".student-list .student",
        submit_name: "students",
        minimum_count_message: "Please select at least one student"
      },
      {
        selector: ".group-project-select",
        submit_name: "project_id",
        use_value: true
      }
    ];

    activator = {
      selector: '#student-group-action:not(.disabled)',
      success: function(){
        $('#student-group-action').removeClass('disabled');
        window.location = '/admin/workgroup/course/' + course_id + '?project_id=' + $('.group-project-select').val();
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

    $('.group-project-select').on('change', function(){
      courseDrag.list_groups_for_selected_project($(this).val());
    });

    $('#generate_assignments').on('click', function(e){
      e.preventDefault();

      $.ajax({
        url: $(this).attr('href'),
        data: {
          'csrfmiddlewaretoken': $.cookie('apros_csrftoken')
        },
        method: 'POST',
        dataType: 'json',
        success: function(data){
          alert(data.message);
        },
        error: function(jqXHR, textStatus, errorThrown){
          var message = textStatus + " - " + errorThrown;
          if(jqXHR.responseJSON){
            message = jqXHR.responseJSON.message;
          }
          else if(jqXHR.responseText){
            message = jqXHR.responseText;
          }
          alert(message);
        }
      });

      return false;
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

    courseDrag.list_groups_for_selected_project($('.group-project-select').val());

  });
