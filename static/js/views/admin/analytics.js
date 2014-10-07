Apros.views.AdminAnalyticsProgress = Backbone.View.extend({
  initialize: function(){
    this.data = [
    {
        "key": "Your Company",
        "values": [
            [
                1,
                0
            ],
            [
                1.5,
                13
            ],
            [
                2,
                24
            ],
            [
                2.5,
                45
            ],
            [
                3,
                57
            ],
            [
                3.5,
                59
            ],
            [
                4,
                63
            ],
            [
                4.5,
                67
            ],
            [
                5,
                72
            ],
            [
                5.5,
                78
            ],
        ]
    },
    {
        "key": "Your Cohort",
        "values": [
            [
                1,
                0
            ],
            [
                1.5,
                12
            ],
            [
                2,
                25
            ],
            [
                2.5,
                46
            ],
            [
                3,
                60
            ],
            [
                3.5,
                65
            ],
            [
                4,
                70
            ],
            [
                4.5,
                80
            ],
            [
                5,
                93
            ],
            [
                5.5,
                100
            ],
        ]
    }];

  },
  render: function() {
    var that = this;
    nv.addGraph(function() {
      var width = 750, height = 350;
      var chart = nv.models.cumulativeLineChart()
                    .x(function(d) { return d[0] })
                    .y(function(d) { return d[1]/100 }) //adjusting, 100% is 1.00, not 100 as it is in the data
                    .color(['#3384CA', '#B1C2CC'])
                    .useInteractiveGuideline(true)
                    .width(width).height(height)
                    ;

       chart.xAxis
          .tickValues([1,2,3,4,5,6])
          .tickFormat(function(d) {
              return d + ' week';
            });

      chart.yAxis
          .tickFormat(d3.format(',.1%'));

      d3.select(that.el)
          .datum(that.data)
          .transition().duration(500).call(chart).style({ 'width': width, 'height': height });

      //TODO: Figure out a good way to do this automatically
      nv.utils.windowResize(chart.update);

      return chart;
    });
  }
})
