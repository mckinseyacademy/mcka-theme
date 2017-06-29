function DashboardCommon(gp_placeholder, lesson_data_base){
    // Value of one of select boxes when no choice is possible due to choices
    // in previous boxes.
    var spinner_identificator_class = "loading-spinner";
    var NONE_DATA_VALUE = "N_A";
    var QUERY_MODES = {
        path: 'path',
        data: 'data',
        company: 'company'
    };


    function make_option(value, text) {
        var option = $("<option>");
        option.val(value);
        option.text(text);
        return option;
    }

    function clear_select_options($target_select) {
        var options = $target_select.find('option:not([data-static])');
        options.remove();
    }

    function get_url_and_data_for_select($target_select, value) {
        var result = {
                url: $target_select.data('filter-endpoint'),
                data: {}
            },
            query_mode = $target_select.data('query-mode') || QUERY_MODES.path;

        switch (query_mode) {
            default:  // intentionally falling through to QUERY_MODES.path - this is the default
            case QUERY_MODES.path:
                result.url = result.url.replace('$value$', value);
                break;
            case QUERY_MODES.data:
                if (value) {
                    result.data[$target_select.data('value-parameter')] = value;
                }
                break;
            case QUERY_MODES.company:
                    result.data["course_id"] = $('select#select-course').find('option:selected').val();
                    result.data["project_id"] = $('select#select-project').find('option:selected').val();
                break;
        }

        return result;
    }

    function update_select_status($select, force_disable) {
        $select.prop('disabled', false);
        if (force_disable || $select.children("option[value='" + NONE_DATA_VALUE + "']").length != 0) {
            $select.prop('disabled', true);
        }
    }

    function parse_response_as_options($select, data) {
        var real_options_count = 0,
            force_disable = false,
            option, last_val;
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            if (item.disabled) {
                continue;
            }
            option = make_option(item.value, item.display_name);
            $select.append(option);
            real_options_count += 1;
            last_val = item.value;
        }

        if (real_options_count == 0) {
            option = make_option(NONE_DATA_VALUE, "None available");
            $select.append(option);
            $select.val(option.val());
        }
        if (real_options_count == 1 && $select.data('autoselect-only-option')) {
            $select.val(last_val);  // last_val is the only actual value in this case
            force_disable = true;
        }
        update_select_status($select, force_disable);
    }

    function show_spinner($target_select) {
        var spinner = $("<i></i>").addClass(spinner_identificator_class).addClass("fa fa-spin fa-spinner");
        spinner.prependTo($target_select.parent());
    }

    function hide_spinner($target_select) {
        $target_select.parent().children("."+spinner_identificator_class).remove();
    }

    return {
        NONE_DATA_VALUE: NONE_DATA_VALUE,

        update_select_status: update_select_status,

        /**
         * Asks target select to update itself  based on a value from
         * a previous select in the chain. Is fired when user updated that previous
         * select or programatically when user selects a quick link.
         * @param $target_select a selector
         * @param value value selected in previous select
         */
        update_select_options: function ($target_select, value) {
            $target_select.prop('disabled', true);
            show_spinner($target_select);

            clear_select_options($target_select);
            $target_select.trigger('change');

            if (!value && !$target_select.data('allow-empty-value')) {
                $target_select.prop('disabled', false);
                hide_spinner($target_select);
                return this.make_resolved_deferred();
            }

            var request_params = get_url_and_data_for_select($target_select, value);
            request_params['method'] = 'GET';

            return $.ajax(request_params).done(function (data) {
                    parse_response_as_options($target_select, data);
                    $target_select.trigger('options_updated');
                })
                .error(this.generic_error_handler)
                .always(function() { hide_spinner($target_select); });
        },

        generic_error_handler: function(xhr, status, error) {
             alert(error);
        },

        make_group_project_element: function(course_id, project_id, company_id) {
            var lesson_data = $.extend({}, lesson_data_base);
            if (!lesson_data.data) {
                lesson_data.data = {};
            }

            lesson_data.courseId = course_id;
            lesson_data.usageId = project_id;
            if (company_id != NONE_DATA_VALUE) {
                lesson_data.data.client_filter_id = company_id;
            }
            else{
                delete lesson_data.data.client_filter_id;
            }
            // This is a hack
            // jquery.xblock doesn't allow to wait until xblock gets fully rendered
            // so we'll just insert an internal div to gp_placeholder
            // so each new xblock will be rendering inside a new div element
            // this element will get detached from DOM, and xblock will not
            // end up showing on webpage.
            var internal_div = $("<div/>");
            gp_placeholder.append(internal_div);
            return internal_div.xblock(lesson_data);
        },

        make_resolved_deferred: function() {
            var def = $.Deferred();
            def.resolve();
            return def;
        }
    }
}