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
      var width = 770, height = 350;
      var maxY = 1;
      var chart = nv.models.cumulativeLineChart()
                    .x(function(d) { return d[0] })
                    .y(function(d) { var y_val = Math.ceil(d[1])/100; maxY = y_val > maxY ? y_val: maxY; return y_val; }) //adjusting, 100% is 1.00, not 100 as it is in the data
                    .color(['#66A5B5', '#B1C2CC'])
                    .useInteractiveGuideline(true)
                    .width(width).height(height)
                    .showControls(false)
                    ;

      var daysNumber = dataJson[0].values.length;
      var lessThanAWeekOld = daysNumber <= 7;
      var tickValues = (lessThanAWeekOld) ? d3.range(0, daysNumber) : d3.range(0, daysNumber, 7);

      chart.xAxis.tickValues(tickValues).tickFormat(function(d) {
          if(daysNumber > 7 && d%7 == 0){
            return (Math.floor(d / 7));
          }
          else if (lessThanAWeekOld) {
            return d;
          }
      });

      chart.lines.forceY([0, maxY]);
      chart.yAxis
          .tickFormat(d3.format(',.1%'));


      for (var property in chart.legend.dispatch) {
          chart.legend.dispatch[property] = function() { };
      }

      d3.select(_this.el)
          .datum(dataJson)
          .transition().duration(500).call(chart).style({ 'width': width, 'height': height });

      d3.select(_this.el)
          .selectAll('.nv-x .nvd3.nv-wrap.nv-axis')
          .append("text")
          .text(function(){return lessThanAWeekOld ? 'days': 'weeks';})
          .attr('y', 15)
          .attr('x', 683);

      d3.selectAll('.nv-background rect')
          .on('click', function() {
          });

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
    // Add empty first entry in dataJson (bug in nv.d3 requires it)
    dataJson[0].values.unshift([0,0]);

    nv.addGraph(function() {
        var width = 805, height = 350;
        var maxY = 1;
        var chart = nv.models.linePlusBarChart()
              .margin({top: 30, right: 60, bottom: 50, left: 70})
              //We can set x data accessor to use index. Reason? So the bars all appear evenly spaced.
              .x(function(d,i) { return i })
              .y(function(d,i) { return d[1]; })
              .width(width).height(height)
              .tooltips(false);

        var daysNumber = dataJson[0].values.length;
        var lessThanAWeekOld = daysNumber <= 7;

        var tickValues = (lessThanAWeekOld) ? d3.range(0, daysNumber) : d3.range(0, daysNumber, 7);

        chart.xAxis.tickValues(tickValues).tickFormat(function(d) {
            if(daysNumber > 7 && d%7 == 0){
              return (Math.floor(d / 7));
            }
            else if (lessThanAWeekOld) {
              return d;
            }
        });

        // force bar chart to start at zero
        var barMax = d3.max(dataJson[0].values, function (d) { return d[1]; });
        chart.bars.forceY([0, barMax || 1]);

        // force line chart to start at zero
        var lineMax = d3.max(dataJson[1].values, function (d) { return d[1]; });
        chart.lines.forceY([0, lineMax || 1]);

        d3.select(_this.el)
          .datum(dataJson)
          .transition()
          .duration(0)
          .call(chart);

        d3.select(_this.el)
            .selectAll('.nv-x .nv-axisMaxMin:last-child')
            .append("text")
            .text(function(){return lessThanAWeekOld ? 'days': 'weeks';})
            .attr('y', 15)
            .attr('x', 10);

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
          .attr("y",790)
          .attr("dy", ".35em")
          ;

        return chart;
    });
  }
})
