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

  style_y_axis: function(selector) {
    var pass_grade = this.chart_data()[0].pass_grade;
    var svg = d3.select(selector);
    svg.selectAll('.nv-y .tick').each(function(d, i) {
      if (d == pass_grade) {
        d3.select(this).attr('class', 'tick major threshold');
      }
      if (i % 2 == 0) {
        d3.select(this).attr('class', 'tick minor');
      }
    });

    svg.select('.nv-y .nv-axis')
      .insert('rect', 'g')
      .attr('x', 0)
      .attr('y', 0)
      .attr('class', 'threshold-rect')
      .attr('width', svg.select('.nv-y line').attr('x2'))
      .attr('height', this.chart.yAxis.scale()(pass_grade));
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
          .showValues(true)
          .transitionDuration(250)
          .forceY([10,100])
          .margin({bottom: 100});

      chart.yAxis.tickValues(_.range(10,110,10));
      chart.yAxis.tickFormat(function(val){
        return val%20 == 0 ? val : '';
      });
      _this.load_chart_data(selector);
      _this.word_wrap_labels(selector);
      _this.style_y_axis(selector);


      d3.select(selector + ' .nv-x.nv-axis > g')
        .selectAll('g')
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr("class", "x-axis-label")


      var temp = d3.selectAll(selector + ' .nv-bar rect')

      //temp.style('fill', 'none');
      var tempSize = temp[0][4].length
        //.selectAll('g')

        console.log(temp[0].nextSibling);

        temp.style('stroke', function(d,i){
          return i == tempSize - 1? 'red' : 'blue';
        })
        
        temp.style('stroke-dasharray', function(d,i){
          return i == tempSize - 1? '5,5' : '2,2';
        })

        temp.style('stroke-width', function(d,i){
          return i == tempSize - 1? '4' : '1';
        })

        
        //temp.showValues(true);

        //console.log(chart.xAxis);
        console.log(temp);



      nv.utils.windowResize(chart.update);
      return chart;
    });
  }
});
