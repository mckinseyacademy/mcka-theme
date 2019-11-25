$(function() {
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
            categories: [''],
            min: 0,
            max: (totalRows+2),
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
                var tooltipHTML = '';
                var now = new Date();

                var new_tab = (this.point.tile_type == 1 || this.point.tile_type == 6);

                if (this.point.label){
                    tooltipHTML += '<div style="padding: 2px; font-size: 7pt; font-weight:600; text-transform: uppercase; color:#868685;">' + 
                        this.point.label + '</div>';
                }
                else {
                    tooltipHTML += '<div>&nbsp;</div>';
                }

                if (this.point.publish_date > now) {
                    tooltipHTML += '<div style="padding: 2px; display: inline-block; height: 55px; margin-top: 5px; font-size: 10pt; color:#868685;">'
                        +this.point.name
                        +'</div>'
                } else {
                    tooltipHTML += '<a href="'
                        + this.point.link
                        + '" style="padding: 2px; display: inline-block; height: 55px; margin-top: 5px; font-size: 10pt; color:#3384ca;"'
                        + (this.point.publish_date < now ? ' class="published"' : ' class="not-published"')
                        + (new_tab ? ' target="_blank">':'>')
                        + this.point.name
                        + '</a>';
                }

                tooltipHTML += '<div style="padding: 2px; font-size: 7pt; font-style: italic; color:#868685">'
                            + (this.point.note ? this.point.note + "</br>" : "");

                switch (this.point.tile_type) {
                    case '1' :
                        tooltipHTML += '</br> </div>';
                        return tooltipHTML;
                        break;
                    case '2':
                    case '3':
                    case '4':
                        if (this.point.track_progress){
                            var progressValue = {'value': this.point.user_progress};
                            var progressText = gettext('Your Progress: %(value)s%');
                            tooltipHTML += interpolate(progressText,progressValue,true) + '</br> </div>';
                        } else {
                            tooltipHTML += '</div>';
                        }
                        return tooltipHTML;
                        break;
                    case '5':
                        if (this.point.track_progress){
                            tooltipHTML += '</br>'
                                + (this.point.user_progress == 100 ? gettext("Complete") :gettext("Incomplete"))
                                + '</div>';
                        } else {
                            tooltipHTML += '</div>';
                        }
                        return tooltipHTML;
                        break;
                    case '6':
                    case '7':
                        tooltipHTML += '</div>';
                        return tooltipHTML;
                        break;
                }
            },
            positioner: function (labelWidth, labelHeight, point) {
                var tooltipX, tooltipY;

                if (point.plotX + labelWidth + 115 > chart.plotWidth) {
                    if (point.plotX + 50 > chart.plotWidth) {
                        tooltipX = Math.abs(point.plotX) + chart.plotLeft - labelWidth - 80 - (point.plotX - chart.plotWidth);
                    } else {
                        if (point.plotX > 0) {
                            tooltipX = Math.abs(point.plotX) + chart.plotLeft - labelWidth - 20;
                        } else {
                            tooltipX = point.plotX + chart.plotLeft - labelWidth - 20;
                        }
                    }
                } else {
                    if (point.plotX < 0) {
                        tooltipX = chart.plotLeft + 80;
                    }
                    else if (point.plotX < 100) {
                        tooltipX = Math.abs(point.plotX) + chart.plotLeft + 70;
                    }
                    else {
                        tooltipX = Math.abs(point.plotX) + chart.plotLeft;
                    }
                }

                if (point.plotY + labelHeight - 15 > chart.plotHeight) {
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
            name: gettext('In Person Session'),
            borderRadius: 24,
            data: dataIPS,
            minPointLength: 48,
            pointWidth: 48,
            dataLabels: {
                inside: true,
                enabled: true,
                useHTML: true,
                verticalAlign: 'middle',
                align: 'center',
                formatter: function() {
                    return "<span class='sr-only'>"+ this.point.sr_label + "</span>" + this.point.fa_icon
                },
                style: {
                    fontSize: '20px'
                }
            }
        },
        {
            name: gettext('Digital Course'),
            borderRadius: 18,
            pointWidth: 48,
            data: dataCourse,
            dataLabels: {
                inside: true,
                enabled: true,
                useHTML: true,
                verticalAlign: 'middle',
                align: 'left',
                fontFamily: '"Open Sans" , sans-serif',
                formatter: function() {
                    if (this.point.isInside) {
                        var labelWidth = this.point.plotLow - this.point.plotHigh
                        if ( this.point.name.length * 7.8 > labelWidth )
                            return "<span class='sr-only'>"+ this.point.sr_label + "</span>" + this.point.name.substr( 0, (labelWidth / 7.8) - 10 ) + "...";
                        return "<span class='sr-only'>"+ this.point.sr_label + "</span>" + this.point.name;
                    }
                    return ''
                },
                style: {
                    fontSize: '15px'
                }
            }
        },
        {
            name: gettext('Group work'),
            data: dataGroup,
            borderRadius: 24,
            minPointLength: 48,
            pointWidth: 48,
            dataLabels: {
                inside: true,
                enabled: true,
                useHTML: true,
                verticalAlign: 'middle',
                align: 'center',
                formatter: function() {
                    return "<span class='sr-only'>"+ this.point.sr_label + "</span>" + this.point.fa_icon
                },
                style: {
                    fontSize: '20px'
                }
            }
        },
        {
            name: gettext('Webinar'),
            data: dataWeb,
            borderRadius: 24,
            minPointLength: 48,
            pointWidth: 48,
            dataLabels: {
                inside: true,
                enabled: true,
                useHTML: true,
                verticalAlign: 'middle',
                align: 'center',
                formatter: function() {
                    return "<span class='sr-only'>"+ this.point.sr_label + "</span>" + this.point.fa_icon
                },
                style: {
                    fontSize: '20px'
                }
            }
        }, 
        {
            name: gettext("Digital Content"),
            data: dataDig,
            borderRadius: 24,
            minPointLength: 48,
            pointWidth: 48,
            dataLabels: {
                enabled: true,
                inside: true,
                useHTML: true,
                verticalAlign: 'middle',
                align: 'center',  
                yLow: -3,
                formatter: function() {
                    return "<span class='sr-only'>"+ this.point.sr_label + "</span>" + this.point.fa_icon
                },
                style: {
                    fontSize: '25px'
                }
            }
        }]
    };

    chart = $('#highcharts-container').highcharts(chartingOptions).highcharts();
});