var stub_historicalBarChart = [
  {
    key: "Lesson Scores",
    values: [
      {
        "label" : "LESSON 1\nASSESSMENT" ,
        "value" : 80,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 2\nASSESSMENT" ,
        "value" : 95,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 3\nASSESSMENT" ,
        "value" : 90,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 4\nASSESSMENT" ,
        "value" : 80,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 5\nASSESSMENT" ,
        "value" : 75,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 6\nASSESSMENT" ,
        "value" : 0,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 7\nASSESSMENT" ,
        "value" : 0,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 8\nASSESSMENT" ,
        "value" : 0,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 9\nASSESSMENT" ,
        "value" : 0,
        "color" : "#becdd6"
      } ,
      {
        "label" : "LESSON 10\nASSESSMENT" ,
        "value" : 0,
        "color" : "#becdd6"
      } ,
      {
        "label" : "FINAL\nASSESSMENT" ,
        "value" : 0,
        "color" : "#becdd6"
      } ,
      {
        "label" : "GROUP WORK\nAVG." ,
        "value" : 95,
        "color" : "#77b4c2"
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
    this.chart = new Apros.models.Chart({chart_data: stub_historicalBarChart});
  },

  render: function() {
    this.chart.historical_bar_chart('#chart-grades svg');
  }
});
