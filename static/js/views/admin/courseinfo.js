Apros.views.ClientAdminCourseInfo = Backbone.View.extend({

  initialize: function(){
    this.render();
  },

  render: function(){
    var dataJson = [
            {
                "week": 1,
                "Not started": 78,
                "In progress": 22,
                "Completed": 0
            },
            {
                "week": 2,
                "Not started": 70,
                "In progress": 25,
                "Completed": 5
            },
            {
                "week": 3,
                "Not started": 60,
                "In progress": 30,
                "Completed": 10
            },
            {
                "week": 4,
                "Not started": 40,
                "In progress": 20,
                "Completed": 40
            },
            {
                "week": 5,
                "Not started": 10,
                "In progress": 35,
                "Completed": 55
            },
            {
                "week": 6,
                "Not started": 5,
                "In progress": 25,
                "Completed": 70
            }
  ];

    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = 860 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var formatPercent = d3.format(".0%");

    var x = d3.scale.linear()
        .domain([1,2,3,4,5,6])
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var color = d3.scale.ordinal().domain([1, 2, 3]).range(['#E37222', '#66A5B5', '#D3D1BA']);

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks([6])
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickFormat(formatPercent);

    var area = d3.svg.area()
        .x(function(d) { return x(d.week); })
        .y0(function(d) { return y(d.y0); })
        .y1(function(d) { return y(d.y0 + d.y); });

    var stack = d3.layout.stack()
        .values(function(d) { return d.values; });

    var svg = d3.select(this.el)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    color.domain(d3.keys(dataJson[0]).filter(function(key) { return key !== "week"; }));

    var percentages = stack(color.domain().map(function(name) {
      return {
        name: name,
        values: dataJson.map(function(d) {
          return {week: d.week, y: d[name] / 100};
        })
      };
    }));

    x.domain(d3.extent(dataJson, function(d) { return d.week; }));

    var percentage = svg.selectAll(".browser")
        .data(percentages)
      .enter().append("g")
        .attr("class", "browser");

    percentage.append("path")
        .attr("class", "area")
        .attr("d", function(d) { return area(d.values); })
        .style("fill", function(d) { return color(d.name); });

    percentage.append("text")
        .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
        .attr("transform", function(d) { return "translate(" + x(d.value.week) + "," + y(d.value.y0 + d.value.y / 2) + ")"; })
        .attr("x", -66)
        .attr("dy", ".35em")
        .text(function(d) { return d.name; });

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);
  }

});
