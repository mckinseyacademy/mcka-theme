var stub_historicalBarChart = [
  {
    key: "Lesson Scores",
    values: [
      {
        "label" : "LESSON 1\nASSESSMENT" ,
        "value" : 80,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 2\nASSESSMENT" ,
        "value" : 95,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 3\nASSESSMENT" ,
        "value" : 90,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 4\nASSESSMENT" ,
        "value" : 80,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 5\nASSESSMENT" ,
        "value" : 75,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 6\nASSESSMENT" ,
        "value" : 0,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 7\nASSESSMENT" ,
        "value" : 0,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 8\nASSESSMENT" ,
        "value" : 0,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 9\nASSESSMENT" ,
        "value" : 0,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "LESSON 10\nASSESSMENT" ,
        "value" : 0,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "FINAL\nASSESSMENT" ,
        "value" : 0,
        "color" : "#b1c2cc"
      } ,
      {
        "label" : "GROUP WORK\nAVG." ,
        "value" : 95,
        "color" : "#66a5b5"
      } ,
      {
        "label" : "TOTAL" ,
        "value" : 75,
        "color" : "#e37121"
      } ,
    ]
  }
];

Apros.views.CourseProgress = Backbone.View.extend({
  initialize: function() {
    var total = _(stub_historicalBarChart[0].values).findWhere({label: 'TOTAL'});
    delete total.label;
    this.chart = new Apros.models.Chart({chart_data: stub_historicalBarChart});
    var el = this.$('#chart-grades').append(
      $('<div />', {'class': 'course-total', html: 'TOTAL<div>' + total.value + '%</div>'})
    );
  },

  render: function() {
    this.chart.historical_bar_chart('#chart-grades svg');
  }
});
