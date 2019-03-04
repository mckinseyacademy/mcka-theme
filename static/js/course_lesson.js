// Show Alert/Close iframes this much seconds before session time out:
const SCORM_ALERT_INTERVAL = 60;
const SCORM_IFRAME_CLOSE_INTERVAL = 30;
const SCORM_IFRAME_CLASS = '.scormxblock_hostframe';
const ALERT_MESSAGE = gettext('It looks like you\'re not active. Click OK to keep working.');
const SCORM_POPUP_IDENTIFIER = 'sco_win';
const SCORM_POPUP_FEATURES = 'alwaysLowered=1';
const REFRESH_SESSION_URL = '/accounts/refresh_user_session';
// Default value is 1800. This is overwritten by course_lessons.haml with the ansible value
var SESSION_TIMEOUT_SECONDS = 1800;

// Launch alerts
function launchAlertTimer() {
    window.setTimeout(function() {
                handleScormAlertTimeout();
                }, (getTimeoutSeconds() - SCORM_ALERT_INTERVAL) * 1000);
}

function launchPopupCloseTimer(){
    window.setTimeout(function() {
                handlePopupCloseTimeout();
                }, (getTimeoutSeconds() - SCORM_IFRAME_CLOSE_INTERVAL) * 1000);
}

// Handle alerts
function handleScormAlertTimeout() {
    if (isTimeOutValid(SCORM_ALERT_INTERVAL)) {
        showAlertOnScormPopup();
    }
    else {
        launchAlertTimer();
    }
}

function handlePopupCloseTimeout() {
    if (isTimeOutValid(SCORM_IFRAME_CLOSE_INTERVAL)) {
        saveScormDataClosePopup();
    }
    else {
        launchPopupCloseTimer();
    }
}

// Scorm spcific tasks
function showAlertOnScormPopup() {
    let scormWindow = getScormPopupReference();
    if (scormWindow) {
        scormWindow.focus();
        let didPressOk = scormWindow.confirm(ALERT_MESSAGE);
        if (didPressOk) {
            refreshUserSession();
        }
    }
}

function saveScormDataClosePopup() {
    // We save scorm data by triggering the set_raw_scorm_status call
    // The call is triggered by changing the 'src' attribute of the iframe(s)
    if (isScormPopupLaunchedBefore()) {
        $(SCORM_IFRAME_CLASS).attr('src', '');
        // Wait 100ms for set_raw_scorm_status(api call) to be fired before removing iframe
        window.setTimeout(function(){
           $(SCORM_IFRAME_CLASS).remove();
           // Wait 400ms for DOM to remove the iframe before popup close attempt is made
           window.setTimeout(function(){
           window.open('', SCORM_POPUP_IDENTIFIER, SCORM_POPUP_FEATURES).close()}, 400);
        }, 100)
    }
}

function getScormPopupReference() {
    //If a popup is open
    if (isScormPopupLaunchedBefore()) {
        // Get a reference to the popup
        var popupReference = window.open('', SCORM_POPUP_IDENTIFIER, SCORM_POPUP_FEATURES);
        // If popup is valid popup launched by the SSLA player
        if (isPopupValid(popupReference)) {return popupReference;}
        // If popup reference is invalid, close invalid popup
        popupReference.close();
    }
    return null;
}

function isScormPopupLaunchedBefore()
{
    // Get all iframes from the page hosted by the scorm xblock with popup as display type
    // non-empty src means the ssla player has been launched (popup was openend)
    var noOfPopupsOpened = $(SCORM_IFRAME_CLASS).filter("iframe[data-display_type='popup'][src!='']").length;
    return (noOfPopupsOpened > 0) ? true : false;
}

// Apros tasks
function refreshUserSession() {
    $.ajax({
      type: 'GET',
      url: REFRESH_SESSION_URL
    }).done( function(data){
        launchAlertTimer();
        launchPopupCloseTimer();
    });
}

function isPopupValid(popupReference)
{
    // If the popup is not the one launched by the SSLA player, it is invalid
    // Invalid popups maybe launched while trying to find the popup launched by user..
    // ..  (which is actually closed by user previously)
    return (popupReference.document.URL === "about:blank") ? false : true;
}

function isTimeOutValid(delta) {
    // Algorithm:
    // *** last_user_interaction
    // .
    // .    (Session active in this interval)
    // .
    // *** last_user_interaction + (session time out seconds - delta)
    // .
    // .    (Session not active in this interval)
    // .

    // Get fres last_user_interaction
    var last_user_interaction = getCookieValue('last_touch')
    if (SESSION_TIMEOUT_SECONDS && last_user_interaction) {
        let current_time = convertToEST(new Date());

        // Delta represents 'Show alert delta seconds before session time out'
        // Add 'session_time_out_seconds' to 'last_user_interaction'
        var session_timeout_delta = moment(last_user_interaction, 'YYYY-MM-DD HH:mm:ss').toDate();
        var session_time_out_seconds_delta = SESSION_TIMEOUT_SECONDS - delta;
        session_timeout_delta.setSeconds(session_timeout_delta.getSeconds() + session_time_out_seconds_delta);

        if (current_time > session_timeout_delta) {
            // Timer is valid
            return true;
        }
        // Else timer is invalid. Return false
    }
    return false;
}

// Util tasks
function getCookieValue(query) {
    var results = document.cookie.match('(^|;)\\s*' + query + '\\s*=\\s*([^;]+)');
    return results ? results.pop().replace(/\"/g, "") : '';
}

function getTimeoutSeconds(){
    // Get seconds to set the next timeout respective of last user touch
    // Get fresh last_user_interaction from cookies
    var last_user_interaction = moment(getCookieValue('last_touch'), 'YYYY-MM-DD HH:mm:ss').toDate();
    let expected_session_timeout = new Date(last_user_interaction.setSeconds(last_user_interaction.getSeconds() + SESSION_TIMEOUT_SECONDS));
    let now = convertToEST(new Date());
    // Subtraction in dates returns in milliseconds, hence dividing by 1000
    let timeOutSeconds = (expected_session_timeout - now)/1000;
    return (timeOutSeconds >= 0) ? timeOutSeconds : 0;
}

function convertToEST(nonEstTime) {
    // EST offset from UTC
    var offset = -5.0;

    // change time offset respective to daylight saving
    if (nonEstTime.isDstObserved()) {
        offset = -4.0;
    }
    // Divide by 60000 to convert to milliseconds
    // convert to UTC
    var utc = nonEstTime.getTime() + (nonEstTime.getTimezoneOffset() * 60000);
    // Then add EST offset
    return new Date(utc + (3600000 * offset));

}

// Functions to handle daylight saving
Date.prototype.stdTimezoneOffset = function () {
    var jan = new Date(this.getFullYear(), 0, 1);
    var jul = new Date(this.getFullYear(), 6, 1);
    return Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset());
}

Date.prototype.isDstObserved = function () {
    return this.getTimezoneOffset() < this.stdTimezoneOffset();
}
