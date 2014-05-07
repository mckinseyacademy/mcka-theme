    $(function(){
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
          $(this).parent().find(selector).toggleClass('expanded').slideToggle();
          el.find('i.caret').toggleClass('fa-caret-down').toggleClass('fa-caret-up');
        });
      }

      accordion($('.select-group-box'), '.group-info.students');

      var removeStudent = function(el, link){
          data = {
            'student' : el.find('.remove-student-icon').attr('name'), 
            'csrfmiddlewaretoken':  $.cookie('apros_csrftoken')
            };
          $.ajax(
          {
            url: link, 
            data: data, 
            method: 'POST'
          }).done(function(data){
              $('div.large-8.columns').html(data);
              $('.student[name="' + el.find('.remove-student-icon').attr('name') + '"]').fadeOut().remove();
              el.find('span.student-count').html(el.find('span.student-count').html() - 1);
              enable_selection(selections, activator);
          });
      }

      $('.remove-student-icon').on('click', function(e){
          e.preventDefault();
          removeStudent($(this).parents('.select-group-box'), $(this).parent('a').attr('href'));
      });

    });