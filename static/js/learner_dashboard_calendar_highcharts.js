$(function() {
    $('#highcharts-container').highcharts({

        chart: {
            type: 'columnrange',
            inverted: true,
            backgroundColor: null
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
            max: dateList[4],
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
                dataLabels: {
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
                    return '<div style="padding: 2px; font-size: 7pt; font-weight: bold; text-transform: uppercase; color:#868685;">' + 
                    this.point.label +  '</div>' + 
                    '<a href="' + this.point.link + '" style="padding: 2px; display: inline-block; height: 65px; margin-top: 5px; font-size: 10pt; color:#3384ca;">' + 
                    this.point.name + '</a>' + '<div style="padding: 2px; font-style: italic; color:#cccccc"></div>';

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
            data: [{
                color: '#e0e0e0',
                name: 'dasads',
                label: 'Course',
                x: 1,
                low: Date.UTC(2016, 07, 01, 4, 0, 0),
                high: Date.UTC(2016, 07, 18, 4, 0, 0)
            }, 
            {
                color: '#e0e0e0',
                name: 'dasads',
                label: 'Course',
                x: 1,
                low: Date.UTC(2016, 08, 14, 0, 0, 0),
                high: Date.UTC(2016, 10, 03, 0, 0, 0)
            }],
            dataLabels: {
                inside: true,
                enabled: true,
                verticalAlign: 'middle',
                align: 'left',
                fontFamily: '"Open Sans" , sans-serif',
                formatter: function() {
                    return 'Digital Content'
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
                inside: true,
                enabled: true,
                verticalAlign: 'middle',
                align: 'center',
                format: '\uf109',
                style: {
                    fontSize: '25px'
                }
            }
        }]
    });
});