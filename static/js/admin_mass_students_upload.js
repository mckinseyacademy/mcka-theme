$(function(){

  var errorsBlockTemplate =
    "<div class='message'><%= data %>" +
      "<div id='user-reg-errors' class='errors'></div></div>";

  var errorsTemplate =
    "<a href='#' data-reveal-id='upload_error_list'>Show Errors</a>" +
    "<ul id='upload_error_list' class='reveal-modal' data-reveal='true'>" +
      "<div class='close-reveal-modal'>" +
        "<i class='fa fa-times-circle'></i>" +
      "</div>" +
      "<% _.each(data.error, function(errorObj, key){ %>" +
        "<li><%= errorObj.fields.error %></li>" +
      "<% }) %>" +
    "</ul>";

  $('#id_student_list, .select-program, .select-course').on("change", function(){
    var program = $('.select-program').find(":selected").val();
    var course = $('.select-course').find(":selected").val();
    if(program != 'select' && course != 'select' && $('#id_student_list').val() != '') {
      $('input[type=submit]').removeAttr('disabled');
    }
  });

  $('.admin-form form').on('click', 'input[type=submit]', function(e){
    e.preventDefault();
    var form = $(this).parent('form');
    var modal = form.parent();
    modal.find('.error').html('');

    var options = {
                url     : form.attr('action'),
                type    : 'POST',
                contentType: false,
                processData: false,
                dataType: 'text',
                cache: false,
                success:function( data ) {
                      data = $.parseJSON(data);
                      var poolingInterval = setInterval(function(){
                        $.ajax({
                          url: form.attr('action') + '/check/' + data.task_key,
                          method: 'GET',
                          dataType: 'json',
                          processData: false,
                          cache: false,
                          'csrfmiddlewaretoken': form.find('[name="csrfmiddlewaretoken"]').val()
                        }).done(function(data){
                          if(data.done == 'done'){
                            clearInterval(poolingInterval);
<<<<<<< 3e39df66d03b221a53ff28f5300117fee9b6eaeb
                            $('#enroll-error-list').html(_.template(errorsBlockTemplate, {'data': data.message}));
                            if(data.error.length > 0){
                              $('#enroll-error-list').find('#user-reg-errors').html(_.template(errorsTemplate, {'data': data}));
                              $("#upload_error_list").foundation('reveal');
                            }
=======
                            $('.upload_results').html(_.template(errorsBlockTemplate, {'data': data.message}));
                            if(data.error.length > 0){
                              $('.upload_results').find('#user-reg-errors').html(_.template(errorsTemplate, {'data': data}));
                              $("#upload_error_list").foundation('reveal');
                            }
                            $('#upload_student_list').foundation('reveal', 'close');
>>>>>>> Mass Student Enroll script
                          }
                          else if(data.done == 'failed'){
                            clearInterval(poolingInterval);
                          }
                          else{
                            $('#attempted').text(data.attempted);
                            $('#succeded').text(data.succeded);
                            $('#failed').text(data.failed);
                          }
                        })
                      }, 10000);
<<<<<<< 3e39df66d03b221a53ff28f5300117fee9b6eaeb
=======
                      $(document).on('closed.fndtn.reveal', '#upload_student_list', function () {
                        if(poolingInterval){
                          clearInterval(poolingInterval);
                        }
                      });
>>>>>>> Mass Student Enroll script
                    },
                error: function( data ){
                      data = $.parseJSON(data);
                      modal.find('.error').append('<p class="warning">Please select file first.</p>');
                    }
                }

    form.ajaxSubmit(options);
  });

});
