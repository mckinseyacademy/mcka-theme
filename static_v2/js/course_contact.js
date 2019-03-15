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
            jQuery.noConflict();
            $('#' + that.attr('id').split('-form')[0]).modal('hide');
            var modal = $('#generalModal');
            modal.find('.modal-title').html(gettext('Notification'));
            modal.find('.modal-body').html(data.message);
            setTimeout(function(){modal.modal('show');}, 350);
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

      $('#contact-ta, #email-member, #email-team').on('show.bs.modal', function () {
        $(this).find('input.button').prop('disabled', 'disabled');
        $(this).find('textarea').val('');
      });
});
