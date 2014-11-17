Apros.views.AdminAnalyticsProgress = Backbone.View.extend({
  initialize: function(options){
    this.options = options;
    var _this = this;
    this.model.setUrl(this.options.client_id, this.options.course_id);
    this.model.fetch({
      success: function(model, response){
        _this.render();
      }
    });
  },
  render: function() {
    var _this = this;

    var dataJson = $.map(_this.model.attributes, function(value, index) {
                    return [value];
                });
    nv.addGraph(function() {
      var width = 750, height = 350;
      var chart = nv.models.cumulativeLineChart()
                    .x(function(d) { return d[0] })
                    .y(function(d) { return Math.ceil(d[1])/100 }) //adjusting, 100% is 1.00, not 100 as it is in the data
                    .color(['#66A5B5', '#B1C2CC'])
                    .useInteractiveGuideline(true)
                    .width(width).height(height)
                    .showControls(false)
                    ;

      var weeksNumber = dataJson[0].values.length;
      var weekslabelsNum = parseInt(weeksNumber / 6) > 1 ? parseInt(weeksNumber / 6) : 1;

      chart.xAxis
          .tickValues(Array.apply(null, {length: dataJson[0].values.length}).map(Number.call, Number))
          .tickFormat(function(d) {
              if((d%weekslabelsNum) == 0  && d != 0 && weekslabelsNum != 1){
                return Math.ceil(d / 7) + ' week';
              }
              else if(weekslabelsNum == 1){
                return d + ' day';
              }
            });

      chart.yAxis
          .tickFormat(d3.format(',.1%'));

      d3.select(_this.el)
          .datum(dataJson)
          .transition().duration(500).call(chart).style({ 'width': width, 'height': height });

      return chart;
    });
  }
})



Apros.views.AdminAnalyticsParticipantActivity = Backbone.View.extend({

  initialize: function(options){
    this.options = options;
    var _this = this;
    this.model.setUrl(this.options.client_id, this.options.course_id);
    this.model.fetch({
      success: function(model, response){
        _this.render();
      }
    });
  },

  render: function() {
    var _this = this;

    var dataJson = $.map(_this.model.attributes, function(value, index) {
                    return [value];
                });

    nv.addGraph(function() {
        var chart = nv.models.linePlusBarChart()
              .margin({top: 30, right: 60, bottom: 50, left: 70})
              //We can set x data accessor to use index. Reason? So the bars all appear evenly spaced.
              .x(function(d,i) { return i })
              .y(function(d,i) { return d[1] })
              .tooltips(false);

        var weeks = d3.range(0, dataJson[0].values.length, 7)
        chart.xAxis.tickValues(weeks).tickFormat(function(d) {
          return 1 + Math.floor(d / 7);
        });


        d3.select(_this.el)
          .datum(dataJson)
          .transition()
          .duration(0)
          .call(chart);

        d3.select(_this.el)
          .selectAll('.nv-x .nv-axisMaxMin:last-child>text')
          .text('weeks')

        d3.select(_this.el)
          .append("text")
          .text("ACTIVITY")
          .attr("transform", "rotate(-90)")
          .attr("x", -200)
          .attr("y", 30)
          .attr("dy", ".35em")
          ;

        d3.select(_this.el)
          .append("text")
          .text("PARTICIPANTS")
          .attr("transform", "rotate(-90)")
          .attr("x", -220)
          .attr("y",910)
          .attr("dy", ".35em")
          ;

        return chart;
    });
  }
})
