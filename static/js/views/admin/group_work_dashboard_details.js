function group_project_dashboard_details(dashboard_configuration) {
    var gp_placeholder = dashboard_configuration['gp_placeholder'];
    var lesson_data_base = dashboard_configuration['lesson_data_base'];
    var user_search_parameters = {
        timeout: 1000, // ms
        timeout_handle: null
    };

    function make_group_project_element() {
        var lesson_data = $.extend({}, lesson_data_base);
        lesson_data.data = {
            client_filter_id: $('select#company_filter').val(),
            activate_block_id: Apros.getParameterByName('activate_block_id')
        };

        return gp_placeholder.xblock(lesson_data);
    }

    function trigger_search_event() {
        var search_criteria = $("#user_search").val();
        $(document).trigger('group_project_v2.details_view.search', search_criteria);
    }

    function trigger_search_clear_event() {
        $(document).trigger('group_project_v2.details_view.search_clear');
    }

    make_group_project_element('{{course.id}}', '{{project.id}}');

    $(document).ready(function () {
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