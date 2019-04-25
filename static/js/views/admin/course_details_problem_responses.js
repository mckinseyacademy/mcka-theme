Apros.views.AdminCourseDetailsProblemResponsesBulk = Backbone.View.extend({
  events: {
    'click #downloadResponsesButton': 'requestReport',
    'click #viewBlocksListButton': 'viewBlocksGrid',
    'click #downloadReportsHistoryButton': 'viewReportsGrid'
  },
  initialize: function (options) {
    this.courseId = options.courseId;
    this.blocksView = options.blocksView;
    this.reportsView = options.reportsView;
  },
  requestReport: function () {
    if ($('#downloadResponsesButton').hasClass('disabled'))
      return;
    let _this = this;
    let selectedRows = this.blocksView.courseBlocksListViewGrid.selectedRows;
    let selectAll = this.blocksView.allBlocksSelected();
    let problem_location = selectAll ? 'course' : selectedRows.join(',');
    let url = ApiUrls.course_reports(this.courseId);
    let data = {'problem_location': problem_location};
    let options = {
      url: url,
      contentType: 'application/x-www-form-urlencoded',
      data: data,
      type: 'POST'
    };
    options.headers = {'X-CSRFToken': $.cookie('apros_csrftoken')};
    $.ajax(options)
      .done(function (data) {
        if (data.status === 'OK') {
          _this.reportsView.collection.fetch();
          _this.reportsView.collection.scheduleRefresh(10000, true);
        } else {
          console.warn('Got unrecognized task request status ' + data.status);
        }
      })
      .fail(function (data) {
        $('#courseBlocksGridWrapper .errorMessage').text('Failed to submit report request');
      });
    $('#reponseGenerateEmailModal').foundation('reveal', 'open');
  },
  viewReportsGrid: function() {
    this.reportsView.render();
    this.reportsView.collection.fetch({
      success: function () {
        $('i.fa-spinner').hide();
      }
    });
    $('#downloadResponsesButton, #courseBlocksGrid, #downloadReportsHistoryButton').hide();
    $('#courseProblemResponseReportsGrid').show();
    // Use inline-block for consistency
    $('#viewBlocksListButton').css('display', 'inline-block');
  },
  viewBlocksGrid: function(){
    this.reportsView.collection.cancelRefresh();
    $('#viewBlocksListButton, #courseProblemResponseReportsGrid').hide();
    $('#courseBlocksGrid').show();
    // Use inline-block for consistency
    $('#downloadResponsesButton, #downloadReportsHistoryButton').css('display', 'inline-block');
  }
});
