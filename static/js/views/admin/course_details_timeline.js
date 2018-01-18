Apros.views.AdminCourseDetailsTimeline = Backbone.View.extend({
  initialize: function(options){
    this.options = options;
    var _this = this;
    this.model.setUrl(this.options.course_id);
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
          .text(function(){return lessThanAWeekOld ? gettext('days'): gettext('weeks');})
          .attr('y', 15)
          .attr('x', 683);

      d3.selectAll('.nv-background rect')
          .on('click', function() {
          });

      return chart;
    });
  }
})
