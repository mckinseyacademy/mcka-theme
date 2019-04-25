// submits forms via ajax and re-renders the html

$('form#program-form.admin-form').submit(function (event) {
    var headers, url,
        programId = $("p[name=program_id").text(),
        form = $(this), data;
    headers = {
        'X-CSRFToken': $.cookie('apros_csrftoken')
    };
    if (programId !== "") {
        url = "/admin/programs/" + programId + "/edit";
    }
    else {
        url = "/admin/programs/program_new";
    }
    data = form.serialize();
    event.preventDefault();
    $.ajax({
        url: url,
        headers: headers,
        method: 'POST',
        dataType: "json",
        data: data,
        success: function (response) {
            if (response.status === 201 || response.status === 200) {
                window.location = response.redirect_url
            }
        },
        error: function (response) {
            if (response.status === 400) {
                var displayName = $('.error[data-name="display_name"]');
                var name = $('.error[data-name="name"]');
                displayName.addClass('hidden').text('');
                name.addClass('hidden').text('');
                data = $.parseJSON(response.responseText);
                errors = data['errors'];
                if (errors.hasOwnProperty('display_name')) {
                    displayName.removeClass('hidden');
                    displayName.text(data['errors']['display_name'][0]);
                }
                if (errors.hasOwnProperty('name')) {
                    name.removeClass('hidden');
                    name.text(data['errors']['name'][0]);
                }
            }
        }
    });
});

