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
	var el = $("#assessment-grade-tracker-patch");
	var data = {"type":"data", "assessment-attempt-count":el.attr("data-attempt-count"),
	"assessment-attempt-max":el.attr("data-attempt-max"), "assessment-score":el.attr("data-attempt-score")};
	SendMessageToSCORMShell(JSON.stringify(data));
}
