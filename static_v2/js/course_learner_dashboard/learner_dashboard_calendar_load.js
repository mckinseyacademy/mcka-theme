$(window).on('load', function() {
    var calendarElem = $('a#open-calendar');
    var ldID = $('#replace-calendar').data("learner-dashboard-id");

    function loadCalendar(){
        if(calendarElem.hasClass('opened'))
            return;
        
        var headers = {
            'X-CSRFToken': $.cookie('apros_csrftoken')
        };

        $.ajax({
            headers: headers,
            type: 'GET',
            url: '/learnerdashboard/' + ldID + '/calendar',
            success: function (data) {
                $('#replace-calendar').html(data.html);
                calendarElem.addClass('opened');
            },
            error: function (xhr, status, error) {
                var err = eval("(" + xhr.responseText + ")");
                console.log(err);
            }
        });

    }

    if (ldID){
        calendarElem.on('click', loadCalendar);
    }

    function nextPrevCalendar(param) {
        var headers = {
          'X-CSRFToken': $.cookie('apros_csrftoken')
        };

        $.ajax({
          headers: headers,
          type: 'GET',
          url: 'learnerdashboard/' + ldID + '/calendar',
          data: param,
          success : function(data) {
            opened = true;
            $('#replace-calendar').html(data.html);
          },
          error: function(xhr, status, error) {
            var err = eval("(" + xhr.responseText + ")");
            console.log (err);
          }
        });
    }

});
