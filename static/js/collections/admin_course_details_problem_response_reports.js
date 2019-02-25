Apros.collections.CourseDetailsProblemResponseReports = Backbone.Collection.extend({
  model: Apros.models.AdminCourseDetailsTaskStatus,
  url: function () {
    return ApiUrls.course_reports();
  },
  parse: function (data) {
    var reports = data.reports;
    var response = [];
    var refreshRequired = false;
    _.each(reports, function (report) {
      report.id = report.task_id;
      if (report.status === 'PROGRESS') {
        refreshRequired = true;
      }
      response.push(report);
    }, this);
    if (refreshRequired) {
      this.scheduleRefresh(60000);
    }
    return response;
  },
  scheduleRefresh: function (timeout, force) {
    if (this.refreshTimeout && !force) {
      return;
    }
    this.cancelRefresh();
    var _this = this;
    this.refreshTimeout = setTimeout(function () {
      _this.cancelRefresh();
      _this.fetch({remove: false});
    }, timeout);
  },
  cancelRefresh: function () {
    clearTimeout(this.refreshTimeout);
    this.refreshTimeout = null;
  }
});
