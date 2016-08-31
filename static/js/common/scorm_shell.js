window.onmessage = function(e){
    if (e.data == 'is_scorm_shell') {
        $(document).trigger("scorm_shell_activate");
        SCORM_SHELL = true;
        console.log("SCORM shell present");
    }
};

function SendMessageToSCORMShell(message)
{
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