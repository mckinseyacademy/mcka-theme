function DashboardCommon(){
     // Value of one of select boxes when no choice is possible due to choices
    // in previous boxes.
    var NONE_DATA_VALUE = "N_A";
    var QUERY_MODES = {
        path: 'path',
        data: 'data'
    };

    function make_option(value, text) {
        var option = $("<option>");
        option.val(value);
        option.html(text);
        return option;
    }

    function clear_select_options($target_select) {
        var options = $target_select.find('option:not([data-static])');
        options.remove();
    }

    function get_url_and_data_for_select($target_select, value) {
        var result = {
                url: $target_select.data('chained-filter-endpoint'),
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
        }

        return result;
    }

    function update_select_status($select, force_disable) {
        $select.removeAttr('disabled');
        if (force_disable || $select.children("option[value='" + NONE_DATA_VALUE + "']").length != 0) {
            $select.attr('disabled', true);
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
            clear_select_options($target_select);
            $target_select.trigger('change');

            if (!value && !$target_select.data('allow-empty-value')) {
                return this.make_resolved_deferred();
            }

            var request_params = get_url_and_data_for_select($target_select, value);
            request_params['method'] = 'GET';

            return $.ajax(request_params).done(
                function (data) {
                    parse_response_as_options($target_select, data);
                    $target_select.trigger('options_updated');
                }
            ).error(this.generic_error_handler);
        },

        generic_error_handler: function(xhr, status, error) {
             alert(error);
        },

        make_resolved_deferred: function() {
            var def = $.Deferred();
            def.resolve();
            return def;
        }
    }
}