/* global $ */

/**
 * Periodically check if the user is logged in, and redirect to course
 * if they have.
 */
function autoRedirectOnLogin() {
  // Repeatedly call an authenticated API to check if the user is logged.
  $.get('/api/user/v1/me').then(function (data) {
      // User is logged in, reload the page so that the user gets
      // redirected to the course.
      setTimeout(function () {
        document.location.reload();
      }, 500);
    }
  ).fail(function () {
      // The user isn't logged in yet.
      setTimeout(autoRedirectOnLogin, 2000);
    }
  );
}

/**
 * Open a popup window for completing the login process.
 * @param url
 * @returns {Window}
 */
function openLoginPopup(url) {
  localStorage.setItem('redirect_after_scorm_login', true);
  var popupWindow = window.open(url, '_blank', 'width=600,height=800,status=no,toolbar=no,location=no,scrollbars=yes');
  if (popupWindow) popupWindow.focus();
  console.log($.cookie());
  return popupWindow;
}

$(document).ready(function () {
  var redirect = $('#access-key-script').data('redirect-to');

  $('#scorm-login-launch').click(function () {
    openLoginPopup(redirect);
    autoRedirectOnLogin();
  });

  // Check if running in an iframe. If it's running in an iframe,
  // we are probably in a SCORM shell
  if (window !== window.parent) {
    $('.normal-access').hide();
    $('.scorm-access').show();
    var popupWindow = openLoginPopup(redirect);
    // If the browser blocks the popup, a null will be returned here.
    // Change the message to indicate that the popup failed to open.
    if (!popupWindow) {
      $('.popups-allowed').hide();
      $('.popups-blocked').show();
    }
    autoRedirectOnLogin();
  } else {
    setTimeout(function () {
      window.location = redirect;
    }, 2000);
  }
});
