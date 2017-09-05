/*
Helper method for checking status of a background task
 */
function checkTaskStatus(taskId, progressElement, loadingImage, callback){
    var interval_id = setInterval(function(){
        var options = {
            url: ApiUrls.admin_bulk_task,
            data: {'task_id':taskId},
            type: "GET"
        };
        options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
        $.ajax(options)
        .done(function(data, textStatus, xhr) {
          if (xhr.status === 200)
          {
            $(progressElement).text('Progress: ' + data['values'].progress + '%');
            if (data['values'].completed == 1)
            {
              $(loadingImage).addClass('hidden');
              clearInterval(interval_id);

              callback(data);
            }
            if (data['error_list'].length > 0)
            {
              console.log(data['error_list']);
            }
          }
        })
        .fail(function(data) {
          console.log("Ajax failed to fetch data");
          console.log(data);
          });
    }, 3000);

    return interval_id;
}
