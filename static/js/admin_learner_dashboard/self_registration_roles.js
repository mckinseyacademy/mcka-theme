var wrapper = $(".role_option"); //Fields wrapper
var add_button = $(".add_field_button"); //Add button ID

$(add_button).click(function(e){
    var total_roles = parseInt($('#count_roles').val()) +1;
    $('#count_roles').val(total_roles);
    e.preventDefault();
    $(wrapper).append('<div class="small-12 new_role" ><div class="small-11 columns">' +
        '<input placeholder="'+gettext("Add new role e.g CEO,CTO")+'" type="text" name="role'+total_roles+'" />' +
      '</div><div class="small-1 columns"><a title="'+gettext("Delete Role")+'" href="#" class="remove_field small-3">' +
        '<i class="fa fa-times"></a></div></div>');
});

$(wrapper).on("click",".remove_field", function(e){
    e.preventDefault();
    $(this).closest('.new_role').remove();
});

$(".remove_role").on("click", function(e){
    e.preventDefault();
    var that = this;
    var headers = {
        'X-CSRFToken': $.cookie('apros_csrftoken')
    };
    $.ajax({
        headers: headers,
        dataType: 'json',
        data: {
          role_id: e.target.id
        },
        type: 'DELETE',
        url: '/admin/course_run/edit',
          success: function(resp) {
              if (resp.status==200){
                  append_msg_and_set_time_out(resp.message)
                  $(that).closest('.edit_role_option').remove();
              }
              else if(resp.status==400){
                  append_msg_and_set_time_out(resp.message)
              }
          }
    })
});

$(".edit_role").on("click", function(e){
    e.preventDefault();
    var that = this;
    var headers = {
        'X-CSRFToken': $.cookie('apros_csrftoken')
    };
    $.ajax({
        headers: headers,
        dataType: 'json',
        data: {
          role_id: e.target.id,
          role_text: $(that).parent('div').prev().find('#created_roles').val()
        },
        type: 'POST',
        url: '/admin/course_run/edit',
          success: function(resp) {
              if(resp.status==200){
                  append_msg_and_set_time_out(resp.message)
                  $(that).parent('div').addClass("hidden");
              }
              else if(resp.status==400){
                  append_msg_and_set_time_out(resp.message)
              }
          }
    })
});

function append_msg_and_set_time_out(message){
    $('<p class="message"> '+ message +'</p>').appendTo('.edit-del-role');
      setTimeout(function() {
            $('.message').remove();
        }, 5000);
}

$(document).on("click", '#created_roles', function(e){
 e.preventDefault();
 var ele = $(this).parent('div')
 ele.next().removeClass("hidden");
 });
