Apros.views.AdminAnalyticsProgress = Backbone.View.extend({
  initialize: function(){
    this.ProgressData = [
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
          .datum(that.ProgressData)
          .transition().duration(500).call(chart).style({ 'width': width, 'height': height });

      //TODO: Figure out a good way to do this automatically
      nv.utils.windowResize(chart.update);

      return chart;
    });
  }
})



Apros.views.AdminAnalyticsParticipantActivity = Backbone.View.extend({
  initialize: function(){
    this.ActivityData = [

    {
        "key": "# Completed modules",
        "bar": true,
        "color": "#3384CA",
        "values": [
            [
                1136005200000,
                1271000
            ],
            [
                1138683600000,
                1271000
            ],
            [
                1141102800000,
                1271000
            ],
            [
                1143781200000,
                0
            ],
            [
                1146369600000,
                0
            ],
            [
                1149048000000,
                0
            ],
            [
                1151640000000,
                0
            ],
            [
                1154318400000,
                0
            ],
            [
                1156996800000,
                0
            ],
            [
                1159588800000,
                3899486
            ],
            [
                1162270800000,
                3899486
            ],
            [
                1164862800000,
                3899486
            ],
            [
                1167541200000,
                3564700
            ],
            [
                1170219600000,
                3564700
            ],
            [
                1172638800000,
                3564700
            ],
            [
                1175313600000,
                2648493
            ],
            [
                1177905600000,
                2648493
            ],
            [
                1180584000000,
                2648493
            ],
            [
                1183176000000,
                2522993
            ],
            [
                1185854400000,
                2522993
            ],
            [
                1188532800000,
                2522993
            ],
            [
                1191124800000,
                2906501
            ],
            [
                1193803200000,
                2906501
            ],
            [
                1196398800000,
                2906501
            ],
            [
                1199077200000,
                2206761
            ],
            [
                1201755600000,
                2206761
            ],
            [
                1204261200000,
                2206761
            ],
            [
                1206936000000,
                2287726
            ],
            [
                1209528000000,
                2287726
            ],
            [
                1212206400000,
                2287726
            ],
            [
                1214798400000,
                2732646
            ],
            [
                1217476800000,
                2732646
            ],
            [
                1220155200000,
                2732646
            ],
            [
                1222747200000,
                2599196
            ],
            [
                1225425600000,
                2599196
            ],
            [
                1228021200000,
                2599196
            ],
            [
                1230699600000,
                1924387
            ],
            [
                1233378000000,
                1924387
            ],
            [
                1235797200000,
                1924387
            ],
            [
                1238472000000,
                1756311
            ],
            [
                1241064000000,
                1756311
            ],
            [
                1243742400000,
                1756311
            ],
            [
                1246334400000,
                1743470
            ],
            [
                1249012800000,
                1743470
            ],
            [
                1251691200000,
                1743470
            ],
            [
                1254283200000,
                1519010
            ],
            [
                1256961600000,
                1519010
            ],
            [
                1259557200000,
                1519010
            ],
            [
                1262235600000,
                1591444
            ],
            [
                1264914000000,
                1591444
            ],
            [
                1267333200000,
                1591444
            ],
            [
                1270008000000,
                1543784
            ],
            [
                1272600000000,
                1543784
            ],
            [
                1275278400000,
                1543784
            ],
            [
                1277870400000,
                1309915
            ],
            [
                1280548800000,
                1309915
            ],
            [
                1283227200000,
                1309915
            ],
            [
                1285819200000,
                1331875
            ],
            [
                1288497600000,
                1331875
            ],
            [
                1291093200000,
                1331875
            ],
            [
                1293771600000,
                1331875
            ],
            [
                1296450000000,
                1154695
            ],
            [
                1298869200000,
                1154695
            ],
            [
                1301544000000,
                1194025
            ],
            [
                1304136000000,
                1194025
            ],
            [
                1306814400000,
                1194025
            ],
            [
                1309406400000,
                1194025
            ],
            [
                1312084800000,
                1194025
            ],
            [
                1314763200000,
                1244525
            ],
            [
                1317355200000,
                475000
            ],
            [
                1320033600000,
                475000
            ],
            [
                1322629200000,
                475000
            ],
            [
                1325307600000,
                690033
            ],
            [
                1327986000000,
                690033
            ],
            [
                1330491600000,
                690033
            ],
            [
                1333166400000,
                514733
            ],
            [
                1335758400000,
                514733
            ]
        ]
    },
    {
        "key": "# of Participants",
        "color": "#E37222",
        "values": [
            [
                1136005200000,
                71.89
            ],
            [
                1138683600000,
                75.51
            ],
            [
                1141102800000,
                68.49
            ],
            [
                1143781200000,
                62.72
            ],
            [
                1146369600000,
                70.39
            ],
            [
                1149048000000,
                59.77
            ],
            [
                1151640000000,
                57.27
            ],
            [
                1154318400000,
                67.96
            ],
            [
                1156996800000,
                67.85
            ],
            [
                1159588800000,
                76.98
            ],
            [
                1162270800000,
                81.08
            ],
            [
                1164862800000,
                91.66
            ],
            [
                1167541200000,
                84.84
            ],
            [
                1170219600000,
                85.73
            ],
            [
                1172638800000,
                84.61
            ],
            [
                1175313600000,
                92.91
            ],
            [
                1177905600000,
                99.8
            ],
            [
                1180584000000,
                121.191
            ],
            [
                1183176000000,
                122.04
            ],
            [
                1185854400000,
                131.76
            ],
            [
                1188532800000,
                138.48
            ],
            [
                1191124800000,
                153.47
            ],
            [
                1193803200000,
                189.95
            ],
            [
                1196398800000,
                182.22
            ],
            [
                1199077200000,
                198.08
            ],
            [
                1201755600000,
                135.36
            ],
            [
                1204261200000,
                125.02
            ],
            [
                1206936000000,
                143.5
            ],
            [
                1209528000000,
                173.95
            ],
            [
                1212206400000,
                188.75
            ],
            [
                1214798400000,
                167.44
            ],
            [
                1217476800000,
                158.95
            ],
            [
                1220155200000,
                169.53
            ],
            [
                1222747200000,
                113.66
            ],
            [
                1225425600000,
                107.59
            ],
            [
                1228021200000,
                92.67
            ],
            [
                1230699600000,
                85.35
            ],
            [
                1233378000000,
                90.13
            ],
            [
                1235797200000,
                89.31
            ],
            [
                1238472000000,
                105.12
            ],
            [
                1241064000000,
                125.83
            ],
            [
                1243742400000,
                135.81
            ],
            [
                1246334400000,
                142.43
            ],
            [
                1249012800000,
                163.39
            ],
            [
                1251691200000,
                168.21
            ],
            [
                1254283200000,
                185.35
            ],
            [
                1256961600000,
                188.5
            ],
            [
                1259557200000,
                199.91
            ],
            [
                1262235600000,
                210.732
            ],
            [
                1264914000000,
                192.063
            ],
            [
                1267333200000,
                204.62
            ],
            [
                1270008000000,
                235
            ],
            [
                1272600000000,
                261.09
            ],
            [
                1275278400000,
                256.88
            ],
            [
                1277870400000,
                251.53
            ],
            [
                1280548800000,
                257.25
            ],
            [
                1283227200000,
                243.1
            ],
            [
                1285819200000,
                283.75
            ],
            [
                1288497600000,
                300.98
            ],
            [
                1291093200000,
                311.15
            ],
            [
                1293771600000,
                322.56
            ],
            [
                1296450000000,
                339.32
            ],
            [
                1298869200000,
                353.21
            ],
            [
                1301544000000,
                348.5075
            ],
            [
                1304136000000,
                350.13
            ],
            [
                1306814400000,
                347.83
            ],
            [
                1309406400000,
                335.67
            ],
            [
                1312084800000,
                390.48
            ],
            [
                1314763200000,
                384.83
            ],
            [
                1317355200000,
                381.32
            ],
            [
                1320033600000,
                404.78
            ],
            [
                1322629200000,
                382.2
            ],
            [
                1325307600000,
                405
            ],
            [
                1327986000000,
                456.48
            ],
            [
                1330491600000,
                542.44
            ],
            [
                1333166400000,
                599.55
            ],
            [
                1335758400000,
                583.98
            ]
        ]
    }

];

  },
  render: function() {
    var that = this;
    nv.addGraph(function() {
        var chart = nv.models.linePlusBarChart()
              .margin({top: 30, right: 60, bottom: 50, left: 70})
              //We can set x data accessor to use index. Reason? So the bars all appear evenly spaced.
              .x(function(d,i) { return i })
              .y(function(d,i) {return d[1] })
              ;

        chart.xAxis.tickFormat(function(d) {
          var dx = that.ActivityData[0].values[d] && that.ActivityData[0].values[d][0] || 0;
          return d3.time.format('%x')(new Date(dx))
        });

        chart.y1Axis
            .tickFormat(d3.format(',f'));

        chart.y2Axis
            .tickFormat(function(d) { return '$' + d3.format(',f')(d) });

        chart.bars.forceY([0]);

        d3.select(that.el)
          .datum(that.ActivityData)
          .transition()
          .duration(0)
          .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
  }
})
