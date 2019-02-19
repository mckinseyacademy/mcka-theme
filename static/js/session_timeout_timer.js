$(function(){
  // Launch a timer that expires on session timeout
  // last_touch in cookie will be none if user is logged out
  if (getCookieValue('last_touch') != 'None') {
    $(function(){
      launchSessionTimeoutTimer();
    })
  }

  function launchSessionTimeoutTimer() {
    window.setTimeout(function() {
        handleAprosSessionTimeout();
    }, getTimeoutSeconds() * 1000);
  }

  function handleAprosSessionTimeout() {
    // When timer expires, check its validity
    if (isTimeoutValid()) {
      window.alert(gettext('You were logged out due to inactivity. Please log back in to continue.'));
      window.location = '/accounts/login/';
    }
    else {
      launchSessionTimeoutTimer();
    }
  }

  function getTimeoutSeconds() { //** Moment changes
    // At any instance, get seconds to set the next timeout respective of last user touch
    // Get fresh last_user_interaction from cookies
    var last_user_interaction = new Date(getCookieValue('last_touch'));
    // Extra 5 seconds added to keep timer sage from client side js thread lags, timing inconsistencies
    let expected_session_timeout = new Date(last_user_interaction.setSeconds(last_user_interaction.getSeconds() + apros_session_timeout_seconds + 5));
    let now = new Date(moment.tz('EST').format('YYYY-MM-DD HH:mm:ss'));
    // Subtraction in dates returns in milliseconds, hence dividing by 1000
    let timeOutSeconds = (expected_session_timeout - now)/1000;
    return (timeOutSeconds >= 0) ? timeOutSeconds : 0;
    }

    function isTimeoutValid() {
    // The timer is valid if current time is 'apros_session_timeout_seconds' more than the 'last_touch'
    var last_user_interaction = getCookieValue('last_touch');
    if (apros_session_timeout_seconds && last_user_interaction) {
      // Get EST time using moment.js
      let current_time = new Date(moment.tz('EST').format('YYYY-MM-DD HH:mm:ss'));
      // Add 'session_time_out_seconds' to 'last_user_interaction'
      var session_timeout_delta = new Date(last_user_interaction);
      var session_time_out_seconds_delta = apros_session_timeout_seconds; // **Remove this
      session_timeout_delta.setSeconds(session_timeout_delta.getSeconds() + apros_session_timeout_seconds);
      // last_user_interaction is deleted from cookies when one tab redirects to login page
      // The second condition is for more than one tabs
      if (current_time > session_timeout_delta || last_user_interaction == "None") {
          // Timer is valid
          return true;
      }
        // Else timer is invalid. Return false
    }
    return false;
  }

  function getCookieValue(query) {
    var results = document.cookie.match('(^|;)\\s*' + query + '\\s*=\\s*([^;]+)');
    return results ? results.pop() : '';
  }

})
