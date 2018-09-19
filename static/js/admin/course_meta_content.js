/* global noMlMsg, noLlMsg */
$(function () {
    var lessonLabelInput = $('#lesson_label');
    var moduleLabelInput = $('#module_label');
    var originalLl = lessonLabelInput.val();
    var originalMl = moduleLabelInput.val();


    function switchMlMode(mode) {
        $('.ml-setup').removeClass('edit-mode-ml add-mode-ml save-mode-ml').addClass(mode + '-mode-ml');
        $('.module-label-input .read-only-ml').text(originalMl || noMlMsg);
        if (mode === 'save') {
            moduleLabelInput.focus();
        }
    }

    function switchLlMode(mode) {
        $('.ll-setup').removeClass('edit-mode-ll add-mode-ll save-mode-ll').addClass(mode + '-mode-ll');
        $('.lesson-label-input .read-only-ll').text(originalLl || noLlMsg);
        if (mode === 'save') {
            lessonLabelInput.focus();
        }
    }

    function resetMlMode() {
        if (originalMl) {
            switchMlMode('edit');
        } else {
            switchMlMode('add');
        }
    }

    function resetLlMode() {
        if (originalLl) {
            switchLlMode('edit');
        } else {
            switchLlMode('add');
        }
    }

    resetMlMode();
    resetLlMode();

    $('#add-ll, #edit-ll, #add-ml, #edit-ml').click(function (event) {
        event.preventDefault();
        if (event.target.id === "add-ml" || event.target.id === "edit-ml"){
            switchMlMode('save');
        }
        else if (event.target.id === "add-ll" || event.target.id === "edit-ll"){
            switchLlMode('save');
        }
    });

    function setSaveStatus(status, lesson_label_flag, module_label_flag) {
        if (lesson_label_flag) {
            var saveIcon = $("span.status-icon-ll .icon").removeClass();
            lessonLabelInput.removeClass('save-failed');

            if (status === "saving") {
                saveIcon.addClass("icon fa fa-spin fa-spinner");
            }

            if (status === "error") {
                moduleLabelInput.addClass('save-failed');
                saveIcon.addClass("icon fa fa-exclamation-circle");
            }

            if (status === "saved") {
                saveIcon.addClass("icon fa fa-check-circle");
            }
        }

        else if(module_label_flag) {
            var saveIcon = $("span.status-icon-ml .icon").removeClass();
            moduleLabelInput.removeClass('save-failed');

            if (status === "saving") {
                saveIcon.addClass("icon fa fa-spin fa-spinner");
            }

            if (status === "error") {
                moduleLabelInput.addClass('save-failed');
                saveIcon.addClass("icon fa fa-exclamation-circle");
            }

            if (status === "saved") {
                saveIcon.addClass("icon fa fa-check-circle");
            }
        }
    }

    function saveData(id){
        var newLl = lessonLabelInput.val();
        var newMl = moduleLabelInput.val();
        var lesson_label_flag = false;
        var module_label_flag = false;

        if (id ==="save-ml"){
            module_label_flag = true
        }
        else if(id ==="save-ll"){
            lesson_label_flag = true
        }


        setSaveStatus("saving", lesson_label_flag, module_label_flag);
        var currentPath = window.location.pathname;
        currentPath = currentPath.split("items/")[1];
        var headers = {
        'X-CSRFToken': $.cookie('apros_csrftoken')
        };
        $.ajax({
            headers: headers,
            url: '/admin/api/courses/'+ currentPath +'/edit_course_meta_data/',
            type: 'POST',
            data: {
                lesson_label_flag: lesson_label_flag,
                lesson_label: newLl,
                module_label_flag: module_label_flag,
                module_label: newMl
            }
        }).done(function () {
            setSaveStatus("saved", lesson_label_flag, module_label_flag);
            if(lesson_label_flag){
                originalLl = newLl;
            }
            else if (module_label_flag){
               originalMl = newMl;
            }
            resetLlMode();
            resetMlMode();
        }).fail(function () {
            setSaveStatus("error", lesson_label_flag, module_label_flag);
        });
    }

    function onResetMlEvent(event) {
        event.preventDefault();
        moduleLabelInput.val(originalMl);
        resetMlMode();
        return false;
    }


    function onResetLlEvent(event) {
        event.preventDefault();
        lessonLabelInput.val(originalLl);
        resetLlMode();
        return false;
    }

    function onSaveEvent(event) {
        event.preventDefault();
        saveData(event.target.id);
        return false;
    }

    $("#reset-ml").click(onResetMlEvent);
    $("#save-ml").click(onSaveEvent);

    $("#reset-ll").click(onResetLlEvent);
    $("#save-ll").click(onSaveEvent);

    moduleLabelInput.on('keyup', function (event) {
        // Reset when Escape key pressed
        if (event.keyCode === 27) {
            onResetMlEvent(event);
        }
        // Save when Enter key pressed
        if (event.keyCode === 13) {
            onSaveEvent(event);
        }
    });

    lessonLabelInput.on('keyup', function (event) {
        // Reset when Escape key pressed
        if (event.keyCode === 27) {
            onResetLlEvent(event);
        }
        // Save when Enter key pressed
        if (event.keyCode === 13) {
            onSaveEvent(event);
        }
    });

});

