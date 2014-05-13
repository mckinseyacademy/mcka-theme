    $(function(){
      var course_id = $('#course_id').val(); 
      var data_table = $('.student-list').dataTable({
          paging: false
        });
      selections = [
        {
          selector: ".student-list .student",
          submit_name: "students",
          minimum_count_message: "Please select at least one student"
        }
      ];

      activator = {
        selector: '#student-group-action', 
        success: function(){
          window.location = '/admin/workgroup/course/' + course_id;
        }
      };
      enable_selection(selections, activator);

      var accordion = function(el, selector){
        el.find('.name').on('click', function(){
          var that = $(this);
          that.parent().find(selector).toggleClass('expanded').slideToggle();
          that.find('i.caret').toggleClass('fa-caret-down').toggleClass('fa-caret-up');
        });
      }

      accordion($('.select-group-box'), '.group-info.students');

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
      }

      $('.remove-student-icon').on('click', function(e){
          e.preventDefault();
          removeStudent($(this), $(this).parent('a').attr('href'));
      });

      var updateGroup = function(group, students, url){
        $.ajax({
          url: url, 
          data: {
            students: students, 
            group: group, 
            'csrfmiddlewaretoken':  $.cookie('apros_csrftoken'), 
          }, 
          method: 'POST'
        }).done(function(data){
          if(data.status == 'success'){
            alert('Group successfully updated');
            window.location.reload();
          }
          else {
            alert(data.status);
          }
        });
      }

      $('.update-group').on('click', function(){
        group = $(this).data('group-id');
        url = $(this).data('url');
        var students = new Array();
        $('#student-list tr.student.selected').each(
          function(){
            students.push($(this).attr('id'));
          });
        updateGroup(group, students, url);
      });

    });