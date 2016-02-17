function group_work_dashboard(gp_placeholder, selected_values, lesson_data_base) {
    function clear_select_options(target_selector) {
        var options = $(target_selector).find('option:not([data-static])');
        options.remove();
    }

    function parse_response_as_options($select, data) {
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            var option = $("<option>");
            option.val(item['value']);
            option.html(item['display_name']);
            if (item.disabled) {
                option.attr('disabled', 'disabled');
            }
            $select.append(option);
        }
    }

    function chain_selects(source_select, target_select) {
        // when source_select is updated, it sends ajax requests and populates target_select with values
        $(source_select).on('change', function () {
            clear_select_options(target_select);
            $(target_select).trigger('change');
            var value = $(this).find('option:selected').val();
            if (!value) {
                return;
            }
            var $target_select = $(target_select);
            var url = $target_select.data('chained-filter-endpoint').replace('$value$', value);
            $.ajax({
                method: 'GET',
                url: url
            }).done(
                function (data) {
                    parse_response_as_options($target_select, data);
                    $(target_select).trigger('options_updated');
                    update_display_strip_item($target_select);
                }
            ).error(
                function (xhr, status, error) {
                    alert(error);
                }
            );
        });
    }

    function toggle_run_report(value) {
        var run_report_btn = $(".run-report a");
        var outline = $(".dashboard_displaying_outline");
        if (value) {
            run_report_btn.removeAttr('disabled');
            run_report_btn.removeClass('disabled');
            run_report_btn.attr('href', '/admin/workgroup/course/' + value + '/download_group_projects_report');
        }
        else {
            run_report_btn.attr('disabled', 'disabled');
            run_report_btn.addClass('disabled');
            outline.html("None");
        }
    }

    function make_group_project_element(course_id, project_id, company_id) {
        var lesson_data = $.extend({}, lesson_data_base);
        lesson_data.courseId = course_id;
        lesson_data.usageId = project_id;
        lesson_data.data = {client_filter_id: company_id};

        gp_placeholder.xblock(lesson_data);
    }

    function set_select_value(select_selector, value) {
        $(select_selector).val(value);
        $(select_selector).trigger('change');
    }

    function restore_selection(selected_values) {
        $('select#select-course').one('options_updated', function () {
            set_select_value('select#select-course', selected_values.course_id);
        });

        $('select#select-project').one('options_updated', function () {
            set_select_value('select#select-project', selected_values.project_id);
        });

        set_select_value('select#select-program', selected_values.program_id);
    }

    function update_display_strip_item($source_select) {
        var outline_component_selector = ".dashboard_outline." + $source_select.data('outline-component');
        var selected_option = $source_select.find('option:selected');

        $(outline_component_selector).empty();
        if (selected_option.length) {
            $(outline_component_selector).html(selected_option.text());
        } else {
            $(outline_component_selector).append($("<i class='fa fa-spin fa-spinner'></i>"));
        }
    }

    $(document).ready(function () {
        chain_selects('select#select-program', 'select#select-course');
        chain_selects('select#select-program', 'select#select-company');
        chain_selects('select#select-course', 'select#select-project');

        var $filters = $("select#select-program, select#select-course, select#select-project, select#select-company");

        $filters.on('change', function () {
            update_display_strip_item($(this));
        });
        $filters.each(function (idx, filter) { update_display_strip_item($(filter)); });

        $("select#select-course").on('change', function () {
            var value = $(this).find('option:selected').val();
            toggle_run_report(value);
        });

        $("select#select-project, select#select-company").on('change', function () {
            var project_id = $("select#select-project").val();
            var course_id = $("select#select-course").val();
            var company_id = $("select#select-company").val();
            gp_placeholder.empty();
            if (project_id && course_id) {
                make_group_project_element(course_id, project_id, company_id);
            }
        });

        if (selected_values.project_id) {
            restore_selection(selected_values);
        }
    });
}
