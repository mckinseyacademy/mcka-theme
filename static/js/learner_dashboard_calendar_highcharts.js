$(function() {
    //$('#highcharts-container').highcharts({
    var chart;
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
                pointWidth: 55,
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
                    '<a href="' + this.point.link + '" style="padding: 2px; display: inline-block; height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>' + '<div style="padding: 2px; font-size: 7pt; font-style: italic; color:#868685">' + 
                    Highcharts.dateFormat('%b %e, %Y', this.point.low) + 
                    '</br>' + this.point.location + '</div>';

                else if (this.point.x == 1)
                    return '<div style="padding: 2px; font-size: 7pt; font-weight:600; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' +
                    '<a href="' + this.point.link + '" style="padding: 2px; display: inline-block; height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>' + '<div style="padding: 2px; font-size: 7pt; font-style: italic; color:#868685">' +
                    this.point.user_progress +
                    '</br>' + this.point.cohort_progress + '</div>';

                else if (this.point.x == 2)
                    return '<div style="padding: 2px; font-size: 7pt; font-weight: bold; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' + 
                    '<a href="' + this.point.link + '" style="padding: 2px; display: inline-block; height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>' + '<div style="padding: 2px; font-size: 7pt; font-style: italic; color:#868685">' + 
                    Highcharts.dateFormat('%b %e, %Y', this.point.low) +
                    '</br>' + Highcharts.dateFormat('%H:%M', this.point.low) + '</div>';

                else if (this.point.x == 3)
                    return '<div style="padding: 2px; font-size: 7pt; font-weight: bold; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' + 
                    '<a href="' + this.point.link + '" style="padding: 2px; display: inline-block; height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>';
            },
            positioner: function (labelWidth, labelHeight, point) {
                var tooltipX, tooltipY;
                if (point.plotX + labelWidth + 80 > chart.plotWidth) {
                    tooltipX = point.plotX + chart.plotLeft - labelWidth - 20;
                } else {
                    tooltipX = point.plotX + chart.plotLeft + 20;
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
                },
                formatter: function () {
                    if (this.percentage.toFixed(0) > 0) return this.percentage.toFixed(0);
                    else return '';
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