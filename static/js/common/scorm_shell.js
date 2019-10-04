window.onmessage = function(e){
    try {
        var data = JSON.parse(e.data);
        if (data.type == 'is_scorm_shell') {
            SCORM_API = data;
            SCORM_SHELL = true;
            $(document).trigger("scorm_shell_activate");
            console.log("SCORM shell present");
        }
    } catch (e) {
        var data = e.data;
    }
};

function SendMessageToSCORMShell(message)
{
    window.top.postMessage(message, '*');
}

SCORM_SHELL = false;
SCORM_API={};
SendMessageToSCORMShell('{"type":"detect_scorm_shell"}');

if (typeof COURSE_MAIN_PAGE === "undefined")
    COURSE_MAIN_PAGE = false;

$(document).on("scorm_shell_activate", function()
{
    if(SCORM_SHELL)
    {
        disableLogoutButton();
        if (COURSE_MAIN_PAGE)
        {
            SendGradebookToScormShell();
            SendProgressToScormShell();
            SendCompletionToScormShell();
            SendFullGradebookToScormShell();
        }
    }

});


function disableLogoutButton()
{
    if(isNewUI())
    {
        $('.footer a').attr("href", "javascript:void(0)");
        $('.footer a').addClass("disabled btn-outline-secondary");
    }
    else
    {
        $('.logout a').attr("href", "javascript:void(0)");
        $('.logout a').attr("disabled", true);
    }
}

function isNewUI() {
    return $("body").hasClass("new-theme");
}

function SendScormAssigmentRelevantData()
{
    if (SCORM_SHELL)
    {
        var el = $("#assessment-grade-tracker-patch");
        var data = {"type":"data", "assessment-attempt-count":el.attr("data-attempt-count"),
        "assessment-attempt-max":el.attr("data-attempt-max"), "assessment-score":el.attr("data-attempt-score")};
        SendMessageToSCORMShell(JSON.stringify(data));
    }
}

function PatchGradeXblockTemplate()
{
    var gradeTemplate = $("#xblock-grade-template");
    if (typeof gradeTemplatePatched == "undefined")
      gradeTemplatePatched = false;
    if (gradeTemplate.length && !gradeTemplatePatched)
    {
      var patch = '<div id="assessment-grade-tracker-patch" onload="SendScormAssigmentRelevantData()" data-attempt-score=<%= score %> data-attempt-count=<%= num_attempts %> data-attempt-max=<%= max_attempts %> ></div>';
      gradeTemplate.html(gradeTemplate.html()+patch);
      gradeTemplatePatched = true;
    }
}

function SendProgressToScormShell()
{
    if (!SCORM_API.progress)
        return;

    var options = {
        url: "/courses/"+scorm_data.courseId+"/progress-json",
        type: "GET",
        dataType: "json",
        timeout: 5000,
        beforeSend: function( xhr ) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
        }
    };

    $.ajax(options)
    .done(function(data) {
        console.log(data);
        SendMessageToSCORMShell(JSON.stringify({"type":"data", "progress":data.user_progress, "course_id": scorm_data.courseId}));
    })
    .fail(function(data) {
        console.log("Ajax failed to fetch data");
        console.log(data)
    });
}

function SendGradebookToScormShell()
{
    if (!SCORM_API.score)
        return;

    var options = {
        url: "/courses/"+scorm_data.courseId+"/grades-json",
        type: "GET",
        dataType: "json",
        timeout: 5000,
        beforeSend: function( xhr ) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
        }
    };

    $.ajax(options)
    .done(function(data) {
        console.log(data);
        SendMessageToSCORMShell(JSON.stringify({"type":"data", "gradebook":data, "course_id": scorm_data.courseId}));
    })
    .fail(function(data) {
        console.log("Ajax failed to fetch data");
        console.log(data)
    });
}

function SendCompletionToScormShell()
{
    if (!SCORM_API.completion)
        return;

    var options = {
        url: "/courses/"+scorm_data.courseId+"/completion-json",
        type: "GET",
        dataType: "json",
        timeout: 5000,
        beforeSend: function( xhr ) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
        }
    };

    $.ajax(options)
    .done(function(data) {
        console.log(data);
        SendMessageToSCORMShell(JSON.stringify({"type":"data", "completion":data, "course_id": scorm_data.courseId}));
    })
    .fail(function(data) {
        console.log("Ajax failed to fetch data");
        console.log(data)
    });
}

function SendFullGradebookToScormShell()
{
    if (!SCORM_API.score)
        return;

    var options = {
        url: "/courses/"+scorm_data.courseId+"/gradebook-json",
        type: "GET",
        dataType: "json",
        timeout: 5000,
        beforeSend: function( xhr ) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
        }
    };

    $.ajax(options)
    .done(function(data) {
        console.log(data);
        SendMessageToSCORMShell(JSON.stringify({"type":"data", "full_gradebook":data, "course_id": scorm_data.courseId}));
    })
    .fail(function(data) {
        console.log("Ajax failed to fetch data");
        console.log(data)
    });
}
