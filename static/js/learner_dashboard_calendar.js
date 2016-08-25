$(function() {
    var yourLabels = ["", "August", "September", "October", "November"];
    var monthIndex = 0;

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
            categories: ['', '', '', '', ''],
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
            min: Date.UTC(2016, 07, 01),
            max: Date.UTC(2016, 11, 01),
            gridLineColor: 'transparent',
            gridLineWidth: 0,
            tickPositioner: function() {
                return [this.min, Date.UTC(2016, 08, 01, 0), Date.UTC(2016, 09, 01, 0), Date.UTC(2016, 10, 01, 0), this.max];
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
            formatter: function() {
                return '<b>' + this.x + this.point.name + '</b><br/>' + Highcharts.dateFormat('%e %B %H:%M', this.point.low) +
                ' - ' + Highcharts.dateFormat('%B %e %H:%M', this.point.high) + '<br/>';
            }
        },

        series: [{
            name: 'In Person Session',
            borderRadius: 33,
            data: dataIPS,
            minPointLength: 65,
            pointWidth: 65,
            dataLabels: {
                inside: true,
                enabled: true,
                //useHTML: true,
                verticalAlign: 'middle',
                align: 'center',
                format: 'S',
                style: {
                    fontSize: '25px'
                }
            }
        },
        {
            name: 'Webinar',
            borderRadius: 18,
            data: [{
                name: 'dasads',
                x: 1,
                low: Date.UTC(2016, 07, 01, 4, 0, 0),
                high: Date.UTC(2016, 07, 09, 4, 0, 0)
            }, 
            {
                name: 'dasads',
                x: 1,
                low: Date.UTC(2016, 07, 15, 0, 0, 0),
                high: Date.UTC(2016, 10, 03, 0, 0, 0)
            }]
        }, 
        {
            name: "Digital Content",
            borderRadius: 18,
            data: [{
                name: 'dasads',
                x: 2,
                low: Date.UTC(2016, 08, 04, 1, 0, 0),
                high: Date.UTC(2016, 09, 25, 5, 0, 0)
            }, 
            {
                name: 'dasads',
                x: 2,
                low: Date.UTC(2016, 10, 02, 10, 0, 0),
                high: Date.UTC(2016, 10, 18, 23, 0, 0)
            }],
            minPointLength: 60,
            dataLabels: {
                inside: true,
                enabled: true,
                verticalAlign: 'middle',
                align: 'left',
                format: 'Digital Content',
                style: {
                    fontSize: '15px'
                }
            }
        }, 
        {
            name: 'Example 1',
            borderRadius: 33,
            data: [{
                name: 'dasads',
                x: 3,
                low: Date.UTC(2016, 07, 01, 0, 0, 0),
                high: Date.UTC(2016, 07, 02, 0, 0, 0)
            }, 
            {
                name: 'dasads',
                x: 3,
                low: Date.UTC(2016, 10, 01, 14, 0, 0),
                high: Date.UTC(2016, 10, 02, 14, 0, 0)
            }],
            minPointLength: 65,
            pointWidth: 65,
            dataLabels: {
                inside: true,
                enabled: true,
                //useHTML: true,
                verticalAlign: 'middle',
                align: 'center',
                format: 'D',
                style: {
                    fontSize: '25px'
                }
            }
        }, 
        {
            name: "Example 3",
            borderRadius: 18,
            data: [{
                x: 4,
                low: Date.UTC(2016, 08, 04, 1, 0, 0),
                high: Date.UTC(2016, 09, 25, 5, 0, 0)
            }, 
            {
                x: 4,
                low: Date.UTC(2016, 10, 02, 10, 0, 0),
                high: Date.UTC(2016, 10, 30, 20, 0, 0)
            }],
            minPointLength: 60,
            dataLabels: {
                inside: true,
                enabled: true,
                verticalAlign: 'middle',
                align: 'left',
                format: 'Mini Board',
                style: {
                    fontSize: '15px'
                }
            }
        }]
    });
});