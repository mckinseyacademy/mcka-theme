function group_work_dashboard(dashboard_configuration) {

    var gp_placeholder = dashboard_configuration['gp_placeholder'];
    var selected_values = dashboard_configuration['selected_values'];
    var lesson_data_base = dashboard_configuration['lesson_data_base'];
    var quick_links_endpoint = dashboard_configuration['quick_links_endpoint'];
    var csrf_token = dashboard_configuration['csrf_token'];
    var common = new DashboardCommon(gp_placeholder, lesson_data_base);
    var no_program_functionality = dashboard_configuration['no_program_functionality'];
    // Stores mapping from quick_link_id to quick-link object
    var quick_links = {};

    /**
     * Asks target select to update itself  based on a value from
     * a previous select in the chain. Is fired when user updated that previous
     * select or programatically when user selects a quick link.
     * @param target_select a selector
     * @param value value selected in previous select
     */
    function update_select_options(target_select, value) {
        var $target_select = $(target_select);
        return common.update_select_options($target_select, value).done(function() {
            update_display_strip_item($target_select);
        });
    }

    function chain_selects(source_select, target_select) {
        // when source_select is updated, it sends ajax requests and populates target_select with values
        $(source_select).on('change', function () {
            var value = $(this).find('option:selected').val();
            update_select_options(target_select, value);
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
            outline.html(gettext("None"));
        }
    }

    function set_select_value(select_selector, value) {
        $(select_selector).val(value);
        $(select_selector).trigger('change');
    }

    function restore_selection(selected_values) {
        $('select#select-course').one('options_updated', function () {
            set_select_value('select#select-course', selected_values.courseId);
        });

        $('select#select-project').one('options_updated', function () {
            set_select_value('select#select-project', selected_values.projectId);
        });

        set_select_value('select#select-program', selected_values.programId);
    }

    function update_display_strip_item($source_select) {
        var outline_component_selector = ".dashboard_outline." + $source_select.data('outline-component');
        var selected_option = $source_select.find('option:selected');

        $(outline_component_selector).empty();
        if (selected_option.length) {
            $(outline_component_selector).text(selected_option.text());
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
            return value != common.NONE_DATA_VALUE ? value: '';
        }

        var post_dict = {
            program_id: filter_value($('#select-program').val()),
            course_id: filter_value($('#select-course').val()),
            company_id: filter_value($("select#select-company").val()),
            group_work_project_id: filter_value($("select#select-project").val())
        };

       send_quick_filters_request('POST', post_dict)
           .done(add_quick_filter_row)
           .error(common.generic_error_handler);
    }


    function get_link_id_from_event(evt) {
        return $(evt.target).parents('tr').data('link-id');
    }


    function delete_quick_filter(evt) {
        var link_id = get_link_id_from_event(evt);
        var confirm_mgs = gettext("Do you really want to delete: \n");
        confirm_mgs += render_quick_filter_label(quick_links[link_id]);
        if (!confirm(confirm_mgs)){
            return;
        }
        send_quick_filters_request('DELETE', {}, link_id).done(
            function() {
                remove_quick_filter_row(link_id);
            }
        ).error(common.generic_error_handler)
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
            common.update_select_status($(filter));
        });

        $("#quick-links td a").removeClass('disabled');

        if (no_program_functionality)
        {
            chain_selects('select#select-project', 'select#select-company');
        }
        else
        {
            chain_selects('select#select-program', 'select#select-course');
            chain_selects('select#select-program', 'select#select-company');
        }
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
    function update_select_from_quick_link(selector, value) {
        var $select = $(selector);
        $select.prop('disabled', false);
        $select.children('option').removeProp('selected');
        if (typeof value == 'undefined'){
            value = ''
        } else {
            value = value.id;
        }
        if ($select.children("option[value='" + common.NONE_DATA_VALUE + "']").length > 0){
            value = common.NONE_DATA_VALUE;
            $select.prop('disabled', true);
        }
        $select.val(value);
    }


    /**
     * Updates all selects using a quick link values.
     * @param quick_link
     */
    function set_quick_link_values(quick_link) {
        update_select_from_quick_link('select#select-program', quick_link.program);
        update_select_from_quick_link('select#select-course', quick_link.course);
        update_select_from_quick_link('select#select-project', quick_link.group_work);
        update_select_from_quick_link('select#select-company', quick_link.client);
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
            update_select_options('select#select-course', quick_link.program.id),
            update_select_options('select#select-company', quick_link.program.id)
        ];

        if (typeof quick_link.course !== 'undefined'){
            deferreds.push(update_select_options('select#select-project', quick_link.course.id))
        }


        $.when.apply($, deferreds).done(function () {
            set_quick_link_values(quick_link);
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
            return common.make_group_project_element(course_id, project_id, company_id);
        } else {
            return common.make_resolved_deferred();
        }
    }

    $(document).ready(function () {
        if ($(".admin-dashboard").hasClass("dashboardV2"))
        {
            load_quick_filters();
            $("#save-filter").click(save_quick_filter);
            $("#quick-links").on('click', 'td.delete-filter a', delete_quick_filter);  
            $(document).on("nice_select_generated", function(event, parent_container){
                activate_ui();
                update_select_options('select#select-company'); // populating company filter with all companies
                if (selected_values.projectId) {
                    restore_selection(selected_values);
                }
            });

            CreateNiceAjaxSelect('.small-6.columns.selectContainer', 'courses_list', {'name':'','id':'select-course', "customAttr":'data-outline-component="course"'}, 
                {"value":'', "name": 'Course', 'customAttr':"data-static=true"}, {"force_refresh":true});
        }
        else
        {
            load_quick_filters();

            activate_ui();
            update_select_options('select#select-company'); // populating company filter with all companies

            $("#save-filter").click(save_quick_filter);
            $("#quick-links").on('click', 'td.delete-filter a', delete_quick_filter);

            if (selected_values.projectId) {
                restore_selection(selected_values);
            }
        }
    });
}
