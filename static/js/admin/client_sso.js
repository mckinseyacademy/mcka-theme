/* global noAccessKeysMsg */
$(function () {
    let identityProviderInput = $('#identity_provider');
    let originalIdP = identityProviderInput.val();

    let accessKeyTable = $('.access-key-list').DataTable({
        paging: false,
        order: [],
        dom: 'lrtip',
        language: {
            // Defined in templates/admin/client/sso.haml
            // where this file in included
            emptyTable: noAccessKeysMsg
        }
    });


    $('#access_key_search').on('input',
        Foundation.utils.debounce(
            function () {
                accessKeyTable.search(this.value).draw();
            },
            250  // debounce interval
        )
    );

    function setSaveStatus(status) {
        let saveIcon = $("span.status-icon .icon").removeClass();

        identityProviderInput.removeClass('save-failed');

        if (status === "saving") {
            saveIcon.addClass("icon fa fa-spin fa-spinner");
        }

        if (status === "error") {
            identityProviderInput.addClass('save-failed');
            saveIcon.addClass("icon fa fa-exclamation-circle");
        }

        if (status === "saved") {
            saveIcon.addClass("icon fa fa-check-circle");
        }
    }

    function saveIdP() {
        let newIdP = identityProviderInput.val();

        setSaveStatus("saving");

        $.ajax({
            url: window.location.pathname,
            method: 'POST',
            data: {
                identity_provider: newIdP,
                csrfmiddlewaretoken: $.cookie('apros_csrftoken')
            }
        }).done(function () {
            setSaveStatus("saved");
            originalIdP = newIdP;
        }).fail(function () {
            setSaveStatus("error");
        });
    }

    $("#reset-idp").click(function (event) {
        event.preventDefault();
        identityProviderInput.val(originalIdP);
    });

    $("#save-idp").click(function (event) {
        event.preventDefault();
        saveIdP();
    });

    ajaxify_overlay_form('#new-principal', 'form', enableCopyButton);
    ZeroClipboard.config({swfPath: 'static/js/vendor/ZeroClipboard.swf'});
    var dialog = $('#new-principal');
    dialog.on('change', '#id_program_id', function () {
        var form = dialog.find('form');
        $.ajax({
            method: 'POST',
            url: form.attr('action'),
            data: form.serialize() + '&program_change'
        })
            .done(function (data, status, xhr) {
                form.parent().html(data);
            })
            .fail(function (data, status, error) {
                alert(error);
            });
    });
    $(document).on('opened.fndtn', '[data-reveal]', enableCopyButton);

    function enableCopyButton() {
        var copyBtn = $('#copy-access-key');
        var client = new ZeroClipboard(copyBtn.get(0));
        var tooltip = copyBtn.siblings('.tooltip');
        client.on('aftercopy', function (event) {
            tooltip.show();
        });
        copyBtn.on('mouseout', function (event) {
            tooltip.fadeOut();
        });
    }

    var url = ApiUrls.participant_courses_get_api();
    InitializeAutocompleteInput(url, 'input#id_course_id');

    $(document).on("click", "#create-access-key-course-quick", function () {
        var form = $("#ajaxAccessKeyCreation");
        var submit_button = form.find("#create_access_key");
        form.find("#create_access_key").attr('disabled', "");
        form.find("#create_access_key").addClass('disabled');
        form.find("input#id_name").val("");
        form.find("input#id_course_id").val("");
    });

    $(document).on("change", "#ajaxAccessKeyCreation input", function () {
        var form = $("#ajaxAccessKeyCreation");
        var submit_button = form.find("#create_access_key");
        form.find("#create_access_key").removeAttr('disabled');
        form.find("#create_access_key").removeClass('disabled');
    });

    $(document).on("click", "#create_access_key", function () {
        var form = $("#ajaxAccessKeyCreation");
        var submit_button = form.find("#create_access_key");

        if (submit_button.hasClass("disabled"))
            return;

        var name = form.find("input#id_name").val().trim();
        var course_id_input = form.find("input#id_course_id");
        var course_id = "";
        if (course_id_input.attr("data-id"))
            course_id = course_id_input.attr("data-id");
        else
            course_id = course_id_input.val().trim();

        if (name === "") {
            alert(gettext("You need to enter name!"));
            return;
        }

        if (course_id === "") {
            alert(gettext("You need to enter course ID!"));
            return;
        }

        var dictionaryToSend = {"name": name, "course_id": course_id};

        var options = {
            url: form.find('form.admin-form').attr('action'),
            data: dictionaryToSend,
            type: "POST",
            dataType: "json",
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
            },
        };
        form.find("#create_access_key").attr('disabled', 'disabled');
        form.find("#create_access_key").addClass('disabled');
        $.ajax(options)
            .done(function (data) {
                if (data["status"] == "success") {
                    form.find("#create_access_key").removeAttr('disabled');
                    form.find("#create_access_key").removeClass('disabled');
                    alert(data["msg"]);
                    form.find('.close-reveal-modal').trigger('click');
                    location.reload();
                }
                else if (data["status"] == "error") {
                    alert(data["msg"]);
                    form.find("#create_access_key").removeAttr('disabled');
                    form.find("#create_access_key").removeClass('disabled');
                }
            })
            .fail(function (data) {
                console.log("Ajax failed to fetch data");
                console.log(data);
            })
    });

});
