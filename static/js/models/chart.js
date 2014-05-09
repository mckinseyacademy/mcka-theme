Apros.models.Chart = Backbone.Model.extend({

  chart_data: function() {
    return this.get('chart_data');
  },

  load_chart_data: function(selector) {
    d3.select(selector)
      .datum(this.chart_data())
      .call(this.chart);
  },

  word_wrap_labels: function(selector) {
    d3.select(selector)
      .selectAll('text')
      .each(function(d, i){
        var el = d3.select(this);
        if (_(d).isString()) {
          var lines = d.split('\n');
          el.text('');
          for (var i = 0; i < lines.length; i++) {
            var tspan = el.append('tspan').text(lines[i]);
            if (i > 0) {
              tspan.attr('x', 0).attr('dy', '15');
            }
          }
        }
      });
  },

  historical_bar_chart: function(selector) {
    this.selector = selector;
    var _this = this;
    nv.addGraph(function() {
      var chart;
      _this.chart = chart = nv.models.discreteBarChart()
          .x(function(d) { return d.label })
          .y(function(d) { return d.value })
          .staggerLabels(false)
          .tooltips(false)
          .showValues(false)
          .transitionDuration(250)
          .forceY([0,100])
          .margin({bottom: 100});

      chart.yAxis.tickFormat(d3.format(',.0d'))
      _this.load_chart_data(selector);
      _this.word_wrap_labels(selector);

      d3.select(selector + ' .nv-x.nv-axis > g')
        .selectAll('g')
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr("class", "x-axis-label")

      nv.utils.windowResize(chart.update);
      return chart;
    });
  }
});
