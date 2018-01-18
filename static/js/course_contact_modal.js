$(function(){
      $('#email-team-form, #contact-ta-form, #email-member-form').on('submit', function(e){
        e.preventDefault();
        var that = $(this);
        data = that.serialize();
        data["csrfmiddlewaretoken"] = $.cookie('apros_csrftoken');
        $.ajax(
          {
            url: that.attr('action'),
            method: 'POST',
            data: data
          }).done(function(data){
            $('#' + that.attr('id').split('-form')[0]).foundation('reveal', 'close');
            var modal = $('#generalModal');
            modal.find('.title').html(gettext('Notification'));
            modal.find('.description').html(data.message);
            setTimeout(function(){modal.foundation('reveal', 'open');}, 350);
          })
      });
      $('#email-team-form textarea, #contact-ta-form textarea, #email-member-form textarea').on('keyup',
        function(){
          if($(this).val() == ''){
            $(this).parent('form').find('input.button').prop('disabled', 'disabled');
          }
          else{
            $(this).parent('form').find('input.button').prop('disabled', false);
          }
        });
      $('.email-member').on('click', function(){
        $('#member-email').val($(this).data('member-email'));
      });

      $('#contact-ta, #email-member, #email-team').on('open.fndtn.reveal', function () {
        $(this).find('input.button').prop('disabled', 'disabled');
        $(this).find('textarea').val('');
      });
});
