window.onmessage = function(e){
    try {
        var data = JSON.parse(e.data);
        if (data.type == 'is_scorm_shell') {
            $(document).trigger("scorm_shell_activate");
            SCORM_API = data;
            SCORM_SHELL = true;
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
console.log("sent scorm shell request");
SendMessageToSCORMShell('{"type":"detect_scorm_shell"}');

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

function ParseReviewStep()
{
    if (CheckIfReviewStepVisible())
    {
        var main_xblock = $(".mentoring.themed-xblock");
        var review_xblock = $(".xblock-embedded_student_view-sb-review-score");
        var assessment = review_xblock.find(".grade-result h2").first();
        var score = parseFloat(assessment.text().match(/\d+%?/g).join('.'));
        var attempts_text = main_xblock.find(".submit .attempts").text();
        var attempts_data = attempts_text.match(/\d+\D?/g);
        var data = {"type":"data", "course_id":scorm_data.courseId,"assessment":{"lesson-id":scorm_data.lessonId, 
        "module-id":scorm_data.moduleId, "attempts-count":parseInt(attempts_data[0]),"attempts-max":parseInt(attempts_data[1]),
        "score":score}};
        return data;
    }
    else
        return null;
}

function CheckIfReviewStepVisible()
{
    return $(".xblock-mentoring_view-sb-review-step").is(':visible');
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

