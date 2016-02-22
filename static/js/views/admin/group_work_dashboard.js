function group_work_dashboard(dashboard_configuration) {

    var gp_placeholder = dashboard_configuration['gp_placeholder'];
    var selected_values = dashboard_configuration['selected_values'];
    var lesson_data_base = dashboard_configuration['lesson_data_base'];
    var quick_links_endpoint = dashboard_configuration['quick_links_endpoint'];
    var csrf_token = dashboard_configuration['csrf_token'];

    // Value of one of select boxes when no choice is possible due to choices
    // in previous boxes.
    var NONE_DATA_VALUE = "N_A";

    // Stores mapping from quick_link_id to quick-link object
    var quick_links = {};

    function clear_select_options(target_selector) {
        var options = $(target_selector).find('option:not([data-static])');
        options.remove();
    }

    function make_option(value, text) {
        var option = $("<option>");
        option.val(value);
        option.html(text);
        return option;
    }

    function parse_response_as_options($select, data) {
        var have_real_options = false;
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            if (item.disabled) {
                continue;
            }
            var option = make_option(item.value, item.display_name);
            $select.append(option);
            have_real_options = true;
        }

        if (!have_real_options) {
            var option = make_option(NONE_DATA_VALUE, "None available");
            $select.append(option);
            $select.val(option.val());
        }
        update_select_status($select);
    }

    function update_select_status($select) {
        $select.removeAttr('disabled');
        if ($select.children("option[value='" + NONE_DATA_VALUE + "']").length != 0) {
            $select.attr('disabled', true);
        }
    }

    function generic_error_hander(xhr, status, error) {
         alert(error);
    }

    /**
     * Asks target select to update itself  based on a value from
     * a previous select in the chain. Is fired when user updated that previous
     * select or programatically when user selects a quick link.
     * @param target_select a selector
     * @param value value selected in previous select
     */
    function fire_chained_select(target_select, value) {
        clear_select_options(target_select);

        var $target_select = $(target_select);
        $target_select.trigger('change');
        var url = $target_select.data('chained-filter-endpoint').replace('$value$', value);
        return $.ajax({
            method: 'GET',
            url: url
        }).done(
            function (data) {
                parse_response_as_options($target_select, data);
                $(target_select).trigger('options_updated');
                update_display_strip_item($target_select);
            }
        ).error(generic_error_hander);
    }

    function chain_selects(source_select, target_select) {
        // when source_select is updated, it sends ajax requests and populates target_select with values
        $(source_select).on('change', function () {
            var value = $(this).find('option:selected').val();
            if (!value) {
                return;
            }
            fire_chained_select(target_select, value);
        });
    }

    function toggle_button(button, value) {
        if (value){
            button.removeAttr('disabled');
            button.removeClass('disabled');
        } else {
            button.attr('disabled', 'disabled');
            button.addClass('disabled');
        }
    }

    function toggle_run_report(value) {
        var run_report_btn = $(".run-report a");
        var outline = $(".dashboard_displaying_outline");
        toggle_button(run_report_btn, value);
        if (value) {
            run_report_btn.attr('href', '/admin/workgroup/course/' + value + '/download_group_projects_report');
        } else {
            outline.html("None");
        }
    }

    function make_group_project_element(course_id, project_id, company_id) {
        var lesson_data = $.extend({}, lesson_data_base);
        lesson_data.courseId = course_id;
        lesson_data.usageId = project_id;
        lesson_data.data = {client_filter_id: company_id};
        // This is a hack
        // jquery.xblock doesn't allow to wait until xblock gets fully rendered
        // so we'll just insert an internal div to gp_placeholder
        // so each new xblock will be rendering inside a new div element
        // this element will get detached from DOM, and xblock will not
        // end up showing on webpage.
        var internal_div = $("<div/>");
        gp_placeholder.append(internal_div);
        return internal_div.xblock(lesson_data);
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


    /**
     * Sends an AJAX request for QuickLinks endpoint attaching CSRF and
     * credentials.
     * @param method
     * @param data
     * @param link_id url to use
     * @returns JQuery jxhr object
     */
    function send_quick_filters_request(method, data, link_id) {
        var url =  quick_links_endpoint;
        if (typeof link_id !== 'undefined'){
            url += link_id + '/';
        }
        return $.ajax({
            url: url,
            method: method,
            data: data,
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        })
    }


    /**
     * Loads a list of user's quick links
     */
    function load_quick_filters() {
        send_quick_filters_request('GET').done(
            function(response) {
                $.each(response, function(idx, link) {
                    add_quick_filter_row(link)
                });
            }
        );
    }


    function render_quick_filter_label(quick_link) {
        function create_label_part(object) {
            if (typeof object === 'undefined'){
                return '';
            }
            return ' - ' + object.display_name;
        }

        return quick_link.program.display_name +
            create_label_part(quick_link.course) +
            create_label_part(quick_link.group_work) +
            create_label_part(quick_link.client);
    }

    function add_quick_filter_row(quick_link) {
        // If there alteady is a row for given id just remove it.
        // In such case whole add operation will just move link to the top
        remove_quick_filter_row(quick_link.id);
        quick_links[quick_link.id] = quick_link;
        var tr = $("<tr/>").data("link-id", quick_link.id)
            .append("<td class='delete-filter'><a>x</a></td>")
            .append(
                $("<td class='activate-quick-link'/>")
                    .append($("<a/>").html(
                        render_quick_filter_label(quick_link)
                    ))
            );
        $('#quick-links tbody').prepend(tr);
        if (!$.isEmptyObject(quick_links)){
            $('#quick-links-section').removeClass('hidden');
        }
    }


    function remove_quick_filter_row(link_id) {
        delete quick_links[link_id];
        var row = $("#quick-links tr").filter(function() {
          return $(this).data("link-id") == link_id
        });
        row.remove();
        if ($.isEmptyObject(quick_links)){
            $('#quick-links-section').addClass('hidden');
        }
    }


    function save_quick_filter() {
        function filter_value(value) {
            return value != NONE_DATA_VALUE ? value: '';
        }

        var post_dict = {
            program_id: filter_value($('#select-program').val()),
            course_id: filter_value($('#select-course').val()),
            company_id: filter_value($("select#select-company").val()),
            group_work_project_id: filter_value($("select#select-project").val())
        };

       send_quick_filters_request('POST', post_dict)
           .done(add_quick_filter_row)
           .error(generic_error_hander);
    }


    function get_link_id_from_event(evt) {
        return $(evt.target).parents('tr').data('link-id');
    }


    function delete_quick_filter(evt) {
        var link_id = get_link_id_from_event(evt);
        var confirm_mgs = "Do you really want to delete: \n";
        confirm_mgs += render_quick_filter_label(quick_links[link_id]);
        if (!confirm(confirm_mgs)){
            return;
        }
        send_quick_filters_request('DELETE', {}, link_id).done(
            function() {
                remove_quick_filter_row(link_id);
            }
        ).error(generic_error_hander)
    }


    function toggle_buttons() {
        var value = $("select#select-course").val();
        toggle_run_report(value);
        toggle_button($('#save-filter'), $("select#select-program").val());
    }


    /**
     * This function attaches all listeners to most of the elements on the
     * webpage, these listeners are sometimes detached, see: load_selected_link.
     *
     * Function activate_ui is supposed to be paired with deactivate_ui, that is
     * deactivate deactivates all listeners activate activates.
     */
    function activate_ui() {
       var $filters = $("select#select-program, select#select-course, select#select-project, select#select-company");

        $.each($filters, function(idx, filter) {
            update_select_status($(filter));
        });

        $("#quick-links td a").removeClass('disabled');

        chain_selects('select#select-program', 'select#select-course');
        chain_selects('select#select-program', 'select#select-company');
        chain_selects('select#select-course', 'select#select-project');

        $filters.on('change', function () {
            update_display_strip_item($(this));
        });

        $filters.each(function (idx, filter) { update_display_strip_item($(filter)); });

        $("select#select-program").on('change', function () {
            toggle_buttons();
        });

        $("select#select-course").on('change', function () {
            toggle_buttons();
        });

        $("select#select-project, select#select-company").on(
            'change', function () { update_dashboard(); });

        $("#quick-links").on('click', 'td.activate-quick-link a', load_selected_link);
    }


    /**
     * Detaches all events from selects on the top of the page.
     */
    function deactivate_ui() {
        var $filters = $("select#select-program, select#select-course, select#select-project, select#select-company");
        $filters.off('change');
        $("#quick-links").off('click', 'td.activate-quick-link a');
        $filters.prop('disabled', true);
        $("#quick-links td a").addClass('disabled');
    }


    /**
     * Updates a value inside one of the select boxes.
     * @param selector selector for a select
     * @param value if of option to select
     */
    function update_select(selector, value) {
        var $select = $(selector);
        $select.prop('disabled', false);
        $select.children('option').removeProp('selected');
        if (typeof value == 'undefined'){
            value = ''
        } else {
            value = value.id;
        }
        if ($select.children("option[value='" + NONE_DATA_VALUE + "']").length > 0){
            value = NONE_DATA_VALUE;
            $select.prop('disabled', true);
        }
        $select.val(value);
    }


    /**
     * Updates all selects using a quick link values.
     * @param quick_link
     */
    function update_selects(quick_link) {
        update_select('select#select-program', quick_link.program);
        update_select('select#select-course', quick_link.course);
        update_select('select#select-project', quick_link.group_work);
        update_select('select#select-company', quick_link.client);
    }


    /**
     * This function is called when user activates a quick-link.
     *
     * Logic is as follows:
     *
     * 1. Load a quick link from cache
     * 2. Deactivate event listeners on all select boxes. This needs to be done
     *    as these listeners update "next" select in a chain when user changes
     *    value and in next step we will update values of all select at once.
     * 3. Launch requests to update four selects on the top of the page with
     *    values from quick link
     * 4. Wait until requests from 3 are processed
     * 5. Select proper options on select boxes
     * 6. Launch request to update a dashboard
     * 7. Activate listeners on selects once again.
     *
     * @param evt event object associated with a user click on a quick filter
     *            link.
     */
    function load_selected_link(evt) {
        var link_id = get_link_id_from_event(evt);
        var quick_link = quick_links[link_id];

        deactivate_ui();

        var deferreds = [
            fire_chained_select('select#select-course', quick_link.program.id),
            fire_chained_select('select#select-company', quick_link.program.id)
        ];

        if (typeof quick_link.course !== 'undefined'){
            deferreds.push(fire_chained_select('select#select-project', quick_link.course.id))
        }


        $.when.apply($, deferreds).done(function () {
            update_selects(quick_link);
            var deferred = update_dashboard();
            $.when(deferred).done(function() {
                activate_ui();
                toggle_buttons();
            });
        })
    }


    function update_dashboard() {
        var project_id = $("select#select-project").val();
        var course_id = $("select#select-course").val();
        var company_id = $("select#select-company").val();
        gp_placeholder.empty();
        if (project_id && course_id) {
            return make_group_project_element(course_id, project_id, company_id);
        } else {
            var def = $.Deferred();
            def.resolve();
            return def;
        }
    }

    $(document).ready(function () {
        load_quick_filters();

        activate_ui();

        $("#save-filter").click(save_quick_filter);
        $("#quick-links").on('click', 'td.delete-filter a', delete_quick_filter);

        if (selected_values.project_id) {
            restore_selection(selected_values);
        }
    });
}
