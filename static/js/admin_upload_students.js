$(function(){

  var errorsBlockTemplate =
    "<div class='message'><%= data %>" +
      "<div id='user-reg-errors' class='errors'></div></div>";

  var errorsTemplate =
    "<a href='#' data-reveal-id='upload_error_list'>"+gettext("Show Errors")+"</a>" +
    "<ul id='upload_error_list' class='reveal-modal' data-reveal='true'>" +
      "<div class='close-reveal-modal'>" +
        "<i class='fa fa-times-circle'></i>" +
      "</div>" +
      "<% _.each(data.error, function(errorObj, key){ %>" +
        "<li><%= errorObj.fields.error %></li>" +
      "<% }) %>" +
    "</ul>";

  $('#id_student_list').on("change", function(){
    $('input[type=submit]').removeAttr('disabled');
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
                            $('.upload_results').html(_.template(errorsBlockTemplate, {'data': data.message}));
                            if(data.error.length > 0){
                              $('.upload_results').find('#user-reg-errors').html(_.template(errorsTemplate, {'data': data}));
                              $("#upload_error_list").foundation('reveal');
                            }
                            $('#upload_student_list').foundation('reveal', 'close');
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
                      }, 2000);
                      $(document).on('closed.fndtn.reveal', '#upload_student_list', function () {
                        if(poolingInterval){
                          clearInterval(poolingInterval);
                        }
                      });
                    },
                error: function( data ){
                      data = $.parseJSON(data);
                      modal.find('.error').append('<p class="warning">'+gettext("Please select file first.")+'</p>');
                    }
                }

    form.ajaxSubmit(options);
  });

});
