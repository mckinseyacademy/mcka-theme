$(function() {
    var chart;

    Highcharts.setOptions({
        global: {
            useUTC : false
        }
    });

    var chartingOptions = {
        chart: {
            type: 'columnrange',
            inverted: true,
            backgroundColor: null,
            animation: false
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: ['', '', '', ''],
            labels: {
            enabled: false
        },
        tickLength: 0,
        lineWidth: 0
        },
     
        yAxis: {
            type: 'datetime',
            title: '',
            opposite: true,
            min: dateList[0],
            max: dateList[5],
            gridLineColor: 'transparent',
            gridLineWidth: 0,
            tickPositioner: function() {
                return dateList;
            },
            labels: {
                enabled: false
            }
        },

        plotOptions: {
            columnrange: {
                grouping: false,
                crop: false,
                dataLabels: {
                    crop: false,
                    overflow: 'none',
                    style: {
                        textShadow: false,
                        color: '#FFFFFF'
                    }
                }
            },
            series: {
                animation: false,
                pointWidth: 55
            }
        },

        legend: {
            enabled: false
        },

        credits: {
            enabled: false
        },

        tooltip: {
            useHTML: true,
            backgroundColor: 'white',
            borderRadius: 15,
            formatter: function() {
                if (this.point.x == 0)
                    return '<div style="padding: 2px; font-size: 7pt; font-weight:600; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' + 
                    '<a href="' + this.point.link + '" style="word-break: break-all; padding: 2px; display: inline-block;' + 
                    'height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>' + '<div style="padding: 2px; font-size: 7pt; font-style: italic; color:#868685">' + 
                    Highcharts.dateFormat('%b %e, %Y', this.point.low) + 
                    '</br>' + this.point.location + '</div>';

                else if (this.point.x == 1)
                    return '<div style="padding: 2px; font-size: 7pt; font-weight:600; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' +
                    '<a href="' + this.point.link + '" style="word-break: break-all; padding: 2px; display: inline-block;' +
                    'height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>' + '<div style="padding: 2px; font-size: 7pt; font-style: italic; color:#868685">' +
                    '</br>' +  '</div>';

                else if (this.point.x == 2)
                    return '<div style="padding: 2px; font-size: 7pt; font-weight: bold; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' + 
                    '<a href="' + this.point.link + '" style="word-break: break-all; padding: 2px; display: inline-block; height: 65px;' + 
                    'margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>' + '<div style="padding: 2px; font-size: 7pt; font-style: italic; color:#868685">' + 
                    Highcharts.dateFormat('%b %e, %Y', this.point.low) +
                    '</br>' + Highcharts.dateFormat('%H:%M', this.point.low) + '</div>';

                else if (this.point.x == 3)
                    return '<div style="padding: 2px; font-size: 7pt; font-weight: bold; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' + 
                    '<a href="' + this.point.link + '" target="_blank" style="word-break: break-all; padding: 2px; display: inline-block;' +
                    'height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>';
            },
            positioner: function (labelWidth, labelHeight, point) {
                var tooltipX, tooltipY;
                if (point.plotX + labelWidth + 85 > chart.plotWidth) {
                    tooltipX = Math.abs(point.plotX) + chart.plotLeft - labelWidth - 20;
                } else {
                    tooltipX = Math.abs(point.plotX) + chart.plotLeft + 20;
                }

                if (point.plotY + labelHeight - 20 > chart.plotHeight) {
                    tooltipY = point.plotY + chart.plotTop - labelHeight + 30;
                } else {
                    tooltipY = point.plotY + chart.plotTop - 35;
                }

                return {
                    x: tooltipX,
                    y: tooltipY
                };
            }
        },

        series: [{
            name: 'In Person Session',
            borderRadius: 24,
            data: dataIPS,
            minPointLength: 48,
            pointWidth: 48,
            dataLabels: {
                inside: true,
                enabled: true,
                verticalAlign: 'middle',
                align: 'center',
                format: '\uf0c0',
                style: {
                    fontSize: '20px'
                }
            }
        },
        {
            name: 'Digital Course',
            borderRadius: 18,
            pointWidth: 48,
            data: dataCourse,
            dataLabels: {
                inside: true,
                enabled: true,
                verticalAlign: 'middle',
                align: 'left',
                fontFamily: '"Open Sans" , sans-serif',
                formatter: function() {
                    console.log ('plotLow plotHigh')
                    console.log (this.point.plotLow, this.point.plotHigh);
                    console.log ('point')
                    console.log (this.point);
                    var labelWidth = this.point.plotLow - this.point.plotHigh
                    if ( this.point.name.length * 7.8 > labelWidth )
                        return this.point.name.substr( 0, (labelWidth / 6) - 10 ) + "...";
                    return this.point.name
                },
                style: {
                    fontSize: '15px'
                }
            }
        },
        {
            name: 'Webinar',
            data: dataWeb,
            borderRadius: 24,
            minPointLength: 48,
            pointWidth: 48,
            dataLabels: {
                inside: true,
                enabled: true,
                verticalAlign: 'middle',
                align: 'center',
                format: '\uf03d',
                style: {
                    fontSize: '20px'
                }
            }
        }, 
        {
            name: "Digital Content",
            data: dataDig,
            borderRadius: 24,
            minPointLength: 48,
            pointWidth: 48,
            dataLabels: {
                enabled: true,
                inside: true,
                verticalAlign: 'middle',
                align: 'center',  
                yLow: -3,
                format: '\uf109',
                style: {
                    fontSize: '25px'
                }
            }
        }]
    };
    chart = $('#highcharts-container').highcharts(chartingOptions).highcharts();
});