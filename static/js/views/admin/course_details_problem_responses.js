Apros.views.AdminCourseDetailsProblemResponsesBulk = Backbone.View.extend({
  events: {
    'click #downloadResponses': 'requestReport',
    'click #downloadReportsHistory': 'toggleReportsGrid'
  },
  initialize: function (options) {
    this.courseId = options.courseId;
    this.blocksView = options.blocksView;
    this.reportsView = options.reportsView;
  },
  requestReport: function () {
    if ($('#downloadResponses').hasClass('disabled'))
      return;
    let _this = this;
    let selectedRows = this.blocksView.courseBlocksListViewGrid.selectedRows;
    let problem_location = selectedRows.join(',');
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
          console.warn('Got unrecognised task request status ' + data.status);
        }
      })
      .fail(function (data) {
        $('#courseBlocksGridWrapper .errorMessage').text('Failed to submit report request');
      });
    $('#downloadReportsHistory').trigger('click');
  },
  toggleReportsGrid: function () {
    btn = $('#downloadReportsHistory');
    if (btn.hasClass('secondary')) {
      this.reportsView.collection.cancelRefresh();
      btn.removeClass('secondary');
      $('#courseProblemResponseReportsGrid').hide();
      $('#courseBlocksGrid').show();
    } else {
      this.reportsView.render();
      this.reportsView.collection.fetch({
        success: function () {
          $('i.fa-spinner').hide();
        }
      });
      btn.addClass('secondary');
      $('#courseBlocksGrid').hide();
      $('#courseProblemResponseReportsGrid').show();
    }
  }
});
