    $(function(){
      var course_id = $('#course_id').val();
      selections = [
        {
          selector: ".student-list .student",
          submit_name: "students",
          minimum_count_message: "Please select at least one student"
        }
      ];

      activator = {
        selector: '#student-group-action'
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
              $('div.large-8.columns').html(data);
              $('.student[name="' + el.attr('name') + '"]').fadeOut().remove();
              parent.find('span.student-count').html(el.find('span.student-count').html() - 1);
              enable_selection(selections, activator);
            }
          }).fail();
      }

      $('.remove-student-icon').on('click', function(e){
          e.preventDefault();
          removeStudent($(this), $(this).parent('a').attr('href'));
      });

    });