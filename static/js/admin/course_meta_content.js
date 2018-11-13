var defaultLessonLabelMsg = gettext("Click Add to specify Lesson Label");
var defaultModuleLabelMsg = gettext("Click Add to specify Module Label");
var defaultLessonsLabelMsg = gettext("Click Add to specify Lessons Label");
var defaultModulesLabelMsg = gettext("Click Add to specify Modules Label");

$(function () {
    var lessonLabelInput = $('#custom_lesson_label');
    var moduleLabelInput = $('#custom_module_label');
    var originalLessonLabel = lessonLabelInput.val();
    var originalModuleLabel = moduleLabelInput.val();

    var lessonsLabelInput = $('#custom_lessons_label');
    var modulesLabelInput = $('#custom_modules_label');
    var originalLessonsLabel = lessonsLabelInput.val();
    var originalModulesLabel = modulesLabelInput.val();


    function switchModuleLabelMode(mode) {
        $('.ml-setup').removeClass('edit-mode-ml add-mode-ml save-mode-ml').addClass(mode + '-mode-ml');
        $('.custom-module-label-input .read-only-ml').text(originalModuleLabel || defaultModuleLabelMsg);
        if (mode === 'save') {
            moduleLabelInput.focus();
        }
    }

    function switchModulesLabelMode(mode) {
        $('.msl-setup').removeClass('edit-mode-msl add-mode-msl save-mode-msl').addClass(mode + '-mode-msl');
        $('.custom-modules-label-input .read-only-msl').text(originalModulesLabel || defaultModulesLabelMsg);
        if (mode === 'save') {
            modulesLabelInput.focus();
        }
    }

    function switchLessonLabelMode(mode) {
        $('.ll-setup').removeClass('edit-mode-ll add-mode-ll save-mode-ll').addClass(mode + '-mode-ll');
        $('.custom-lesson-label-input .read-only-ll').text(originalLessonLabel || defaultLessonLabelMsg);
        if (mode === 'save') {
            lessonLabelInput.focus();
        }
    }

    function switchLessonsLabelMode(mode) {
        $('.lsl-setup').removeClass('edit-mode-lsl add-mode-lsl save-mode-lsl').addClass(mode + '-mode-lsl');
        $('.custom-lessons-label-input .read-only-lsl').text(originalLessonsLabel || defaultLessonsLabelMsg);
        if (mode === 'save') {
            lessonsLabelInput.focus();
        }
    }

    function resetModuleLabelMode() {
        if (originalModuleLabel) {
            switchModuleLabelMode('edit');
        } else {
            switchModuleLabelMode('add');
        }
    }

    function resetModulesLabelMode() {
        if (originalModulesLabel) {
            switchModulesLabelMode('edit');
        } else {
            switchModulesLabelMode('add');
        }
    }

    function resetLessonLabelMode() {
        if (originalLessonLabel) {
            switchLessonLabelMode('edit');
        } else {
            switchLessonLabelMode('add');
        }
    }

    function resetLessonsLabelMode() {
        if (originalLessonsLabel) {
            switchLessonsLabelMode('edit');
        } else {
            switchLessonsLabelMode('add');
        }
    }

    function resetMode() {
        resetModuleLabelMode();
        resetModulesLabelMode();
        resetLessonLabelMode();
        resetLessonsLabelMode();
    }

    resetMode();

    $('#add-ll, #edit-ll, #add-ml, #edit-ml, #add-lsl, #edit-lsl, #add-msl, #edit-msl').click(function (event) {
        event.preventDefault();
        if (event.target.id === "add-ml" || event.target.id === "edit-ml"){
            switchModuleLabelMode('save');
        }
        else if (event.target.id === "add-msl" || event.target.id === "edit-msl"){
            switchModulesLabelMode('save');
        }
        else if (event.target.id === "add-ll" || event.target.id === "edit-ll"){
            switchLessonLabelMode('save');
        }
        else if (event.target.id === "add-lsl" || event.target.id === "edit-lsl"){
            switchLessonsLabelMode('save');
        }
    });

    function setSaveStatus(status, lesson_label_flag, module_label_flag, lessons_label_flag, modules_label_flag) {
        if(lesson_label_flag) {
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
        else if(lessons_label_flag) {
            var saveIcon = $("span.status-icon-lsl .icon").removeClass();
            lessonsLabelInput.removeClass('save-failed');

            if (status === "saving") {
                saveIcon.addClass("icon fa fa-spin fa-spinner");
            }

            if (status === "error") {
                lessonsLabelInput.addClass('save-failed');
                saveIcon.addClass("icon fa fa-exclamation-circle");
            }

            if (status === "saved") {
                saveIcon.addClass("icon fa fa-check-circle");
            }
        }

        else if(modules_label_flag) {
            var saveIcon = $("span.status-icon-msl .icon").removeClass();
            modulesLabelInput.removeClass('save-failed');

            if (status === "saving") {
                saveIcon.addClass("icon fa fa-spin fa-spinner");
            }

            if (status === "error") {
                modulesLabelInput.addClass('save-failed');
                saveIcon.addClass("icon fa fa-exclamation-circle");
            }

            if (status === "saved") {
                saveIcon.addClass("icon fa fa-check-circle");
            }
        }
    }

    function saveData(id){
        var lesson_label_flag = false;
        var module_label_flag = false;
        var lessons_label_flag = false;
        var modules_label_flag = false;

        if (id ==="save-ml"){
            module_label_flag = true
        }
        else if(id ==="save-ll"){
            lesson_label_flag = true
        }
        else if(id ==="save-lsl"){
            lessons_label_flag = true
        }
        else if(id ==="save-msl"){
            modules_label_flag = true
        }

        var data = {
            lesson_label_flag: lesson_label_flag,
            lesson_label: lessonLabelInput.val(),
            module_label_flag: module_label_flag,
            module_label: moduleLabelInput.val(),
            lessons_label_flag: lessons_label_flag,
            lessons_label: lessonsLabelInput.val(),
            modules_label_flag: modules_label_flag,
            modules_label: modulesLabelInput.val()
            };
        setSaveStatus("saving", lesson_label_flag, module_label_flag, lessons_label_flag, modules_label_flag);
        var currentPath = window.location.pathname;
        currentPath = currentPath.split("items/")[1];
        var headers = {
        'X-CSRFToken': $.cookie('apros_csrftoken')
        };
        $.ajax({
            headers: headers,
            url: '/admin/api/courses/'+ currentPath +'/edit_course_meta_data/',
            type: 'POST',
            data: data
        }).done(function () {
            setSaveStatus("saved", lesson_label_flag, module_label_flag, lessons_label_flag, modules_label_flag);
            if(lesson_label_flag){
                originalLessonLabel = lessonLabelInput.val();
            }
            else if (module_label_flag){
               originalModuleLabel = moduleLabelInput.val();
            }
            else if (lessons_label_flag){
               originalLessonsLabel = lessonsLabelInput.val();
            }
            else if (modules_label_flag){
               originalModulesLabel = modulesLabelInput.val();
            }
            resetMode()
        }).fail(function () {
            setSaveStatus("error", lesson_label_flag, module_label_flag, lessons_label_flag, modules_label_flag);
        });
    }

    function onResetModuleLabelEvent(event) {
        event.preventDefault();
        moduleLabelInput.val(originalModuleLabel);
        resetModuleLabelMode();
        return false;
    }

    function onResetLessonLabelEvent(event) {
        event.preventDefault();
        lessonLabelInput.val(originalLessonLabel);
        resetLessonLabelMode();
        return false;
    }

    function onResetModulesLabelEvent(event) {
        event.preventDefault();
        modulesLabelInput.val(originalModulesLabel);
        resetModulesLabelMode();
        return false;
    }

    function onResetLessonsLabelEvent(event) {
        event.preventDefault();
        lessonsLabelInput.val(originalLessonsLabel);
        resetLessonsLabelMode();
        return false;
    }

    function onSaveEvent(event) {
        event.preventDefault();
        saveData(event.target.id);
        return false;
    }

    $("#reset-ml").click(onResetModuleLabelEvent);
    $("#save-ml").click(onSaveEvent);

    $("#reset-ll").click(onResetLessonLabelEvent);
    $("#save-ll").click(onSaveEvent);

    $("#reset-msl").click(onResetModulesLabelEvent);
    $("#save-msl").click(onSaveEvent);

    $("#reset-lsl").click(onResetLessonsLabelEvent);
    $("#save-lsl").click(onSaveEvent);

    moduleLabelInput.on('keyup', function (event) {
        // Reset when Escape key pressed
        if (event.keyCode === 27) {
            onResetModuleLabelEvent(event);
        }
        // Save when Enter key pressed
        if (event.keyCode === 13) {
            onSaveEvent(event);
        }
    });

    modulesLabelInput.on('keyup', function (event) {
        // Reset when Escape key pressed
        if (event.keyCode === 27) {
            onResetModulesLabelEvent(event);
        }
        // Save when Enter key pressed
        if (event.keyCode === 13) {
            onSaveEvent(event);
        }
    });

    lessonLabelInput.on('keyup', function (event) {
        // Reset when Escape key pressed
        if (event.keyCode === 27) {
            onResetLessonLabelEvent(event);
        }
        // Save when Enter key pressed
        if (event.keyCode === 13) {
            onSaveEvent(event);
        }
    });

    lessonsLabelInput.on('keyup', function (event) {
        // Reset when Escape key pressed
        if (event.keyCode === 27) {
            onResetLessonsLabelEvent(event);
        }
        // Save when Enter key pressed
        if (event.keyCode === 13) {
            onSaveEvent(event);
        }
    });

});

