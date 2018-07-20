/* global ga */
$(function () {
    ga('send', 'pageview', 'Login', {dimension4: 'new_flow'});

    function getHashedId() {
        let login_id = $("input[name=login_id]").val().trim();
        if (login_id === "") {
            return "";
        }
        let hash_prefix = login_id.indexOf('@') >= 0 ? 'e:' : 'u:';
        return hash_prefix + $.md5(login_id).slice(-20);
    }

    function resetErrors() {
        $('.error').text('');
        $("input[name=login_id]").get(0).setCustomValidity("");
        $("input[name=password]").get(0).setCustomValidity("");
    }

    function resetLoginForm() {
        $(".login-page").removeClass("login-with-password");
        $("input[name=password]").val("");
        resetErrors();
    }

    function loginWithPassword() {
        $("#login-form .username_display .username").html($("input[name=login_id]").val());
        $(".login-page").addClass("login-with-password");
        $("input[name=password]").focus();
    }

    function setError(error) {
        if (error.login_id) {
            $(".login-error").text(error["login_id"]);
            $("input[name=login_id]").get(0).setCustomValidity(error["login_id"]);
        } else if (error.password) {
            $(".password-error").text(error["password"]);
            $("input[name=password]")
                .val("")
                .get(0)
                .setCustomValidity(error["password"]);
        } else {
            $(".error-msg").text(error["error"]);
        }
    }

    function redirectAfterLogin(xhr) {
        function redirect(){
            window.location.href = xhr.getResponseHeader("Location");
        }
        // Wait for analytics events to submit before redirecting
        ga(redirect);
        // If the above doesn't work, redirect in 250ms anyway.
        window.setTimeout(redirect, 250);
    }

    $('#go-back').on('click', function () {
        ga('send', 'event', 'Login', 'navigate', 'back', {
            dimension1: getHashedId(),
            dimension4: 'new_flow',
        });
        resetLoginForm();
    });

    $('form input[type="text"], form input[type="password"]').on('keypress', resetErrors);

    $('#login-form').submit(function (ev) {
        ev.preventDefault();
        resetErrors();

        let passwordLogin = $(".login-page").hasClass("login-with-password");
        let headers = {
            'X-CSRFToken': $.cookie('apros_csrftoken')
        };
        let login_id = $("input[name=login_id]").val();
        let password = $("input[name=password]").val();
        let hashed_id = getHashedId();

        if (passwordLogin) {
            ga('send', 'event', 'Login', 'login', 'normal_login', {
                dimension1: hashed_id,
                dimension4: 'new_flow'
            });
            $.ajax({
                headers: headers,
                data: {login_id: login_id, password: password},
                type: 'POST',
                url: '/accounts/login/',
                success: function (_1, _2, xhr) {
                    ga('send', 'event', 'Login', 'normal_login', 'success', {
                        dimension1: hashed_id,
                        dimension4: 'new_flow'
                    });
                    redirectAfterLogin(xhr);
                },
                error: function (error) {
                    ga('send', 'event', 'Login', 'normal_login', 'failure', {
                        dimension1: hashed_id,
                        dimension4: 'new_flow'
                    });
                    setError(error.responseJSON);
                }
            });
        } else {
            $.ajax({
                headers: headers,
                data: {login_id: login_id, validate_login_id: true},
                type: 'POST',
                url: '/accounts/login/',
                success: function (_1, _2, xhr) {
                    ga('send', 'event', 'Login', 'validate', 'success', {
                        dimension1: hashed_id,
                        dimension4: 'new_flow'
                    });
                    if (xhr.status === 278) {
                        ga('send', 'event', 'Login', 'sso_login', 'redirecting', {
                            dimension1: hashed_id,
                            dimension4: 'new_flow'
                        });
                        redirectAfterLogin(xhr);
                    } else {
                        loginWithPassword();
                    }
                },
                error: function (error) {
                    ga('send', 'event', 'Login', 'validate', 'failure', {
                        dimension1: hashed_id,
                        dimension4: 'new_flow'
                    });
                    setError(error.responseJSON);
                }
            });
        }
    });

    $('a[data-reveal-id="reset-password"]').click(function() {
        ga('send', 'event', 'Login', 'forgot_password', {
            dimension1: getHashedId(),
            dimension4: 'new_flow'
        });
    });

    $('#email-support').click(function () {
        ga('send', 'event', 'Login', 'click_email_support', {
            dimension1: getHashedId(),
            dimension4: 'new_flow'
        });
    });

    if ($('#generalModal input.show-modal').length > 0) {
        $('#generalModal').foundation('reveal', 'open');
    }
    // Preserve hash value in ?next= argument
    if (window.location.hash !== '') {
        var hash = window.location.hash.substr(1);
        if (hash.indexOf('forgot-password-modal') > -1) {
            $('a[data-reveal-id="reset-password"]').click();
            window.location.hash = hash.replace('forgot-password-modal', '');
        }
        else {
            var next_with_hash = $.query.get('next') + window.location.hash,
                query_with_hash = $.query.set('next', next_with_hash).toString();
            window.history.replaceState({}, '', query_with_hash);
        }
    }
    ajaxify_overlay_form('#reset-password', 'form');
});


