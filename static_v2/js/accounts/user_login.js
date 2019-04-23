/* global ga */
$(function () {
    function getHashedId() {
        let login_id = $("input[name=login_id]").val().trim();
        if (login_id === "") {
            return "";
        }
        let hash_prefix = login_id.indexOf('@') >= 0 ? 'e:' : 'u:';
        return hash_prefix + $.md5(login_id).slice(-20);
    }

    function resetErrors() {
        $('.login-error, .password-error').text('');
        $("input[name=login_id]").get(0).setCustomValidity("");
        $("input[name=password]").get(0).setCustomValidity("");
    }

    function resetLoginForm() {
        $(".login-page").removeClass("login-with-password");
        $("input[name=password]").val("");
        resetErrors();
    }

    function loginWithPassword() {
        $("#login-form > div.user_name_element").addClass("success");
        $('.form-group.user_name_element').children('.i.ico-state').html("check_circle");
        $(".login-page").addClass("login-with-password");
        $('.form-group.user_password_element').toggleClass("d-none");
        $("input[name=password]").focus();
        $('.forgot-pswd-link').removeClass('d-none');
        if($("input[name=password]").val() =="")
        {
            $('#login').attr("disabled", "disabled");
        }
    }

    function setError(error) {
        if (error.login_id) {
            $(".login-error").text(error["login_id"]);
            $("#login-form > div.user_name_element").addClass("error");
            $('.form-group.user_name_element').children('i.ico-state').html("error");
            $("input[name=login_id]").get(0).setCustomValidity(error["login_id"]);
        } else if (error.password) {
            $(".password-error").text(error["password"]);
            $("#login-form > div.user_password_element").addClass("error");
            $('.form-group.user_password_element').children('i.ico-state').html("error");
            $("input[name=password]")
                .get(0)
                .setCustomValidity(error["password"]);
        } else if (error.lock_out) {
            $('#user_lock_out_notification').modal('show');
        } else if (error.user_active == false) {
            sendUserActivationEmail();
        } else {
            $(".error-msg").text(error["error"]);
        }
    }

    function redirectAfterLogin(xhr) {
        function redirect() {
            window.location.href = xhr.getResponseHeader("Location");
        }
        // Wait for analytics events to submit before redirecting
        ga(redirect);
        // If the above doesn't work, redirect in 250ms anyway.
        window.setTimeout(redirect, 250);
    }

    $('form input[type="text"], form input[type="password"]').on('keypress', resetErrors);

    $("#login-form").submit(handleLoginFormSubmit);

    // Email has been prefilled, go directly to login-mode.
    if ($("input[name=login_id]").val()) {
        handleLoginFormSubmit();
    }

    $('a[id="resend-email"]').click(function () {
        sendUserActivationEmail()
    });

    function sendUserActivationEmail() {
        const headers = {
            'X-CSRFToken': $.cookie('apros_csrftoken')
        };
        $.ajax({
            headers: headers,
            type: 'GET',
            url: '/mcka-api/v1/send_activation_link/' + $("input[name=login_id]").val(),
            success: function (_1, _2, xhr) {
                openModalWithActivationMessage(xhr)
            },
            error: function (error) {
                openModalWithActivationMessage(error)
            }
        });
    }

    function openModalWithActivationMessage(xhr) {
        $('.headline_message').html("")
        $('.activation_success_message').hide()
        if (xhr.status === 200) {
            $('.headline_message').append(xhr.responseJSON["message"]);
            $('.activation_success_message').show()
        } else {
            $('.headline_message').append(xhr.responseJSON["error"]);
        }
        $('#user_activation_notification').modal("show");
    }

    function handleLoginFormSubmit(ev) {
        ev && ev.preventDefault();
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
                dimension4: hashed_id,
            });
            $.ajax({
                headers: headers,
                data: {
                    login_id: login_id,
                    password: password
                },
                type: 'POST',
                url: '/',
                success: function (_1, _2, xhr) {
                    ga('send', 'event', 'Login', 'normal_login', 'success', {
                        dimension4: hashed_id,
                    });
                    redirectAfterLogin(xhr);
                },
                error: function (error) {
                    ga('send', 'event', 'Login', 'normal_login', 'failure', {
                        dimension4: hashed_id,
                    });
                    setError(error.responseJSON);
                }
            });
        } else {
            $.ajax({
                headers: headers,
                data: {
                    login_id: login_id,
                    validate_login_id: true
                },
                type: 'POST',
                success: function (_1, _2, xhr) {
                    ga('send', 'event', 'Login', 'validate', 'success', {
                        dimension4: hashed_id,
                    });
                    if (xhr.status === 278) {
                        ga('send', 'event', 'Login', 'sso_login', 'redirecting', {
                            dimension4: hashed_id,
                        });
                        redirectAfterLogin(xhr);
                    } else {
                        loginWithPassword();
                    }
                },
                error: function (error) {
                    ga('send', 'event', 'Login', 'validate', 'failure', {
                        dimension4: hashed_id,
                    });
                    setError(error.responseJSON);
                }
            });
        }
    }

    $('a[data-reveal-id="reset-password"]').click(function () {
        $("#user_lock_out_notification").modal("hide");
        $("#password-reset-modal").modal("show");
    });

    $('#email-support').click(function () {
        ga('send', 'event', 'Login', 'click_email_support', {
            dimension4: getHashedId(),
        });
    });

    // Preserve hash value in ?next= argument
    if (window.location.hash !== '') {
        var hash = window.location.hash.substr(1);
        if (hash.indexOf('forgot-password-modal') > -1) {
            $('a[data-reveal-id="reset-password"]').click();
            window.location.hash = hash.replace('forgot-password-modal', '');
        } else {
            var next_with_hash = $.query.get('next') + window.location.hash,
                query_with_hash = $.query.set('next', next_with_hash).toString();
            window.history.replaceState({}, '', query_with_hash);
        }
    }
    ajaxify_overlay_form('#reset-password', 'form');
});
