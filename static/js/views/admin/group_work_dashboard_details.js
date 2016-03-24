function group_project_dashboard_details(dashboard_configuration) {
    var lesson_data_base = dashboard_configuration['lesson_data_base'];

    var common = new DashboardCommon(dashboard_configuration['gp_placeholder'], lesson_data_base);
    var user_search_parameters = {
        timeout: 1000, // ms
        timeout_handle: null
    };

    function make_group_project_element() {
        common.make_group_project_element(
            lesson_data_base.courseId, lesson_data_base.usageId, $('select#company_filter').val()
        );
    }

    function trigger_search_event() {
        var search_criteria = $("#user_search").val();
        $(document).trigger('group_project_v2.details_view.search', search_criteria);
    }

    function trigger_search_clear_event() {
        $(document).trigger('group_project_v2.details_view.search_clear');
    }

    make_group_project_element();

    $(document).ready(function () {
        common.update_select_options($("select#company_filter"), dashboard_configuration.selected_values.programId);

        $('#company_filter').on('change', function () {
            $('.group_project_placeholder').empty();

            make_group_project_element();

            $('.dashboard_outline_wrapper span.dashboard_outline.company').html(
                $('#company_filter').find(':selected').html()
            );
            $("#user_search").val('');
        });

        $("#user_search").keyup(function () {
            if (user_search_parameters.timeout_handle) {
                clearTimeout(user_search_parameters.timeout_handle);
            }
            if ($("#user_search").val().length > 2) {
                user_search_parameters.timeout_handle = setTimeout(trigger_search_event, user_search_parameters.timeout);
            }
            else {
                trigger_search_clear_event();
            }
        });
    });
}