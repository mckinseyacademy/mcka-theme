$(function(){
  // Launch a timer that expires on session timeout
  if (lastTouchExists() && isUserLoggedIn()) {
    $(function(){
      launchSessionTimeoutTimer();
    })
  }

  function lastTouchExists() {
    const lastTouchCookie = getCookieValue('last_touch');
    return lastTouchCookie === 'None' || !lastTouchCookie ? false : true;
  }

  function isUserLoggedIn() {
    return getCookieValue('sessionid') ? true : false;
  }

  function launchSessionTimeoutTimer() {
    window.setTimeout(function() {
        handleAprosSessionTimeout();
    }, getTimeoutSeconds() * 1000);
  }

  function handleAprosSessionTimeout() {
    // When timer expires, check its validity
    if (isTimeOutValid(0)) {
      redirectOnTimeOut();
    }
    else {
      launchSessionTimeoutTimer();
    }
  }

  function redirectOnTimeOut() {
    if (SCORM_SHELL){
        window.parent.close();
    }
    else {
      window.alert(gettext('You were logged out due to inactivity. Please log back in to continue.'));
      window.location = '/accounts/login/';
    }
  }
})

// Util tasks
// In global scope as being used in other files as well (course_lesson.js)
function getCookieValue(query) {
    var results = document.cookie.match('(^|;)\\s*' + query + '\\s*=\\s*([^;]+)');
    return results ? results.pop().replace(/\"/g, "") : '';
}

function getTimeoutSeconds(){
    // Get seconds to set the next timeout respective of last user touch
    // Get fresh last_user_interaction from cookies
    var last_user_interaction = moment(getCookieValue('last_touch'), 'YYYY-MM-DD HH:mm:ss').toDate();
    // 3 seconds offset added to address time inconsistencies/jerks
    var offset = 3
    let expected_session_timeout = new Date(last_user_interaction.setSeconds(last_user_interaction.getSeconds() + apros_session_timeout_seconds + offset));
    let now = moment(moment.tz('UTC').format('YYYY-MM-DD HH:mm:ss.ssss'), 'YYYY-MM-DD HH:mm:ss').toDate();
    // Subtraction in dates returns in milliseconds, hence dividing by 1000
    let timeOutSeconds = (expected_session_timeout - now)/1000;
    return (timeOutSeconds >= 0) ? timeOutSeconds : 0;
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
    if (apros_session_timeout_seconds && last_user_interaction) {
        let current_time = moment(moment.tz('UTC').format('YYYY-MM-DD HH:mm:ss'), 'YYYY-MM-DD HH:mm:ss').toDate();


        // Delta represents 'Show alert delta seconds before session time out'
        // Add 'session_time_out_seconds' to 'last_user_interaction'
        var session_timeout_delta = moment(last_user_interaction, 'YYYY-MM-DD HH:mm:ss').toDate();
        var session_time_out_seconds_delta = apros_session_timeout_seconds - delta;
        session_timeout_delta.setSeconds(session_timeout_delta.getSeconds() + session_time_out_seconds_delta);

        if (current_time > session_timeout_delta) {
            // Timer is valid
            return true;
        }
        // Else timer is invalid. Return false
    }
    return false;
}
