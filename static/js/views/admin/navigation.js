$('.remove_image').click(function (e)
{
  var client_id = $(this).attr('client_id');
  var csrftoken = getCookie('csrftoken');
   var img_type = $(this).attr('type');
  if(confirm(gettext('Are you sure you want to remove this ?')))
  {
     $.ajax({
        url: '/admin/clients/'+ client_id +'/remove_image/',
        type: 'POST',
         headers: {'X-CSRFToken': csrftoken},
        data: {'image_type':img_type},
        success: function(result)
        {
            $('.'+img_type).hide();
        },
         error: function (result)
         {
            $('#removeBrandingImageError h3').html(result.responseJSON.message);
            $('#removeBrandingImageError').foundation('reveal', 'open');
         }

    });
  }

});

$('.closeModal').click(function ()
{
     $('#removeBrandingImageError').foundation('reveal', 'close');
});


function getCookie(name)
{
    var re = new RegExp(name + "=([^;]+)");
    var value = re.exec(document.cookie);
    return (value != null) ? value[1] : null;
}


$(document).ready(function () {
    $('.ui-checker').click(function () {
        debugger;
        if($('.ui-checker').is(':checked')){
            $('.switch-text').text("ON");
        }
        else {
            $('.switch-text').text("OFF");
        }
    });
});
