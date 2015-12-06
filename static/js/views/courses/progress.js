Apros.views.CourseProgress = Backbone.View.extend({
  initialize: function() {
    var total = _(historicalBarChart[0].values).findWhere({label: 'TOTAL'});
    delete total.label;
    this.chart = new Apros.models.Chart({chart_data: historicalBarChart});
    var el = this.$('#chart-grades').append(
      $('<div />', {'class': 'course-total', html: 'TOTAL<div>' + total.value + '%</div>'})
    );
  },

  render: function() {
    this.chart.historical_bar_chart('#chart-grades svg');
  }
});
