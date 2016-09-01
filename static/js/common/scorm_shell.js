window.onmessage = function(e){
    if (e.data == 'is_scorm_shell') {
        $(document).trigger("scorm_shell_activate");
        SCORM_SHELL = true;
        console.log("SCORM shell present");
    }
};

function SendMessageToSCORMShell(message)
{
    if (SCORM_SHELL)
        window.top.postMessage(message, '*');
}
SCORM_SHELL = false;
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
        var attempts_data = attempts_text.match(/\d+?/g);
        var data = {"type":"data", "course_id":scorm_data.courseId,"assessment":{"lesson-id":scorm_data.lessonId, 
        "module-id":scorm_data.moduleId, "assessment-attempt-count":attempts_data[0],"assessment-attempt-max":attempts_data[1], 
        "assessment-score":score}};
        return data;
    }
    else
        return null;
}

function CheckIfReviewStepVisible()
{
    return $(".xblock-mentoring_view-sb-review-step").is(':visible');
}
