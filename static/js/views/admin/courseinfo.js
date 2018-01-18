Apros.views.ClientAdminCourseInfo = Backbone.View.extend({

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

  render: function(){
    var _this = this;

    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = 860 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var formatPercent = d3.format(gettext(".0%"));

    var x = d3.scale.linear()
        .domain([1,2,3,4,5,6])
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var color = d3.scale.ordinal().domain(["Not started", "In progress", "Completed"]).range(['#E37222', '#66A5B5', '#D3D1BA']);

    var dataJson = $.map(_this.model.attributes, function(value, index) {
        return [value];
    });

    var daysNumber = dataJson.length;
    var lessThanAWeekOld = daysNumber <= 7;

    // Add empty first entry in dataJson (first presented day should be day 0 when the course is less than a week old)
    if (lessThanAWeekOld) dataJson.unshift({'Completed': 0, 'In progress': 0, 'Not started': 0, 'day': 0});

    var tickValues = lessThanAWeekOld ? d3.range(0, daysNumber) : d3.range(1, daysNumber, 7);

    var xAxis = d3.svg.axis()
        .scale(x)
        .tickValues(tickValues)
        .tickFormat(function(d){
            if (lessThanAWeekOld) return d + gettext(' day');
            return Math.floor(d / 7) + gettext(' week');
        })
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickFormat(formatPercent);

    function make_x_axis() {
        return d3.svg.axis()
            .scale(x)
             .orient("bottom")
             .ticks(5)
    }

    function make_y_axis() {
        return d3.svg.axis()
            .scale(y)
            .orient("left")
            .ticks(5)
    }

    var area = d3.svg.area()
        .x(function(d) { return x(d.day); })
        .y0(function(d) { return y(d.y0); })
        .y1(function(d) { return y(d.y0 + d.y); });

    var stack = d3.layout.stack()
        .values(function(d) { return d.values; });

    var svg = d3.select(this.el)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var percentages = stack(color.domain().map(function(name) {
      return {
        name: name,
        values: dataJson.map(function(d) {
          return {day: d.day, y: d[name] / 100};
        })
      };
    }));

    x.domain(d3.extent(dataJson, function(d) { return d.day; }));

    var percentage = svg.selectAll(".browser")
        .data(percentages)
      .enter().append("g")
        .attr("class", "browser");

    percentage.append("path")
        .attr("class", "area")
        .attr("d", function(d) { return area(d.values); })
        .style("fill", function(d) { return color(d.name); });

/*    percentage.append("text")
        .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
        .attr("transform", function(d) { return "translate(" + x(d.value.week) + "," + y(d.value.y0 + d.value.y / 2) + ")"; })
        .attr("x", -66)
        .attr("dy", ".35em")
        .text(function(d) { return d.name; }); */

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    svg.append("g")
        .attr("class", "grid")
        .attr("transform", "translate(0," + height + ")")
        .call(make_x_axis()
            .tickSize(-height, 0, 0)
            .tickFormat("")
        )

    svg.append("g")
        .attr("class", "grid")
        .call(make_y_axis()
            .tickSize(-width, 0, 0)
            .tickFormat("")
        )
  }

});
