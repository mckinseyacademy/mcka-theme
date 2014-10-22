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
                    .y(function(d) { return d[1]/100 }) //adjusting, 100% is 1.00, not 100 as it is in the data
                    .color(['#66A5B5', '#B1C2CC'])
                    .useInteractiveGuideline(true)
                    .width(width).height(height)
                    ;

      var weeksNumber = dataJson[0].values.length;
      var weekslabelsNum = parseInt(weeksNumber / 6);

      chart.xAxis
          .tickValues(Array.apply(null, {length: dataJson[0].values.length}).map(Number.call, Number))
          .tickFormat(function(d) {
              if((d%weekslabelsNum) == 0){
                return Math.ceil(d / 7) + ' week';
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
              .y(function(d,i) {return d[1] })
              .tooltips(false)
              ;

        chart.xAxis.tickFormat(function(d) {
          var dx = dataJson[0].values[d] && dataJson[0].values[d][0] || 0;
          return d3.time.format('%x')(new Date(dx))
        });

        chart.bars.forceY([0]);

        d3.select(_this.el)
          .datum(dataJson)
          .transition()
          .duration(0)
          .call(chart);

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
