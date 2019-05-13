function group_work_dashboard_assignment_info() {
    function exportStatsDownloader(){
        $('#courseDetailsMainModal').find('.courseModalTitle').text(gettext('Downloadable Workgroup Completion Report'));
        $('#courseDetailsMainModal').find('.courseModalDescription').text(
            gettext("We'll e-mail you when your report is ready to download.")
        );

        var saveButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges');
        var cancelButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.cancelChanges');

        saveButton.on('click', function () {
            var courseId = $("#workGroupReportContainer").attr("data-id");
            var url = ApiUrls.admin_bulk_task;
            var dictionaryToSend = {
                type:'workgroup_completion_report', course_id: courseId,
            };

            var options = {
                url: url,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(dictionaryToSend),
                processData: false,
                type: "POST",
                dataType: "json"
            };
            options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};

            $.ajax(options)
            .done(function(data, textStatus, xhr) {
                if (xhr.status === 201){
                    $('#courseDetailsMainModal').foundation('reveal', 'close');
                }
            })
            .fail(function(data) {
                $('#courseDetailsMainModal').find('.courseModalDescription').text(
                    gettext("Error initiating the report generation. Please retry later.")
                );
                console.log("Ajax failed to fetch data");
                console.log(data);
            });
        });

        cancelButton.on('click', function () {
            $('#courseDetailsMainModal').foundation('reveal', 'close');
            });

        $('#courseDetailsMainModal').foundation('reveal', 'open');
    }

    $(document).ready(function () {
        $('#workGroupReportContainer').on('click', '.bulkExportStats', function () {
            exportStatsDownloader();
        });
    });
}
