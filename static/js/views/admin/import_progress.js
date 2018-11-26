  Apros.views.ImportProgress = Backbone.View.extend({
      pollingParams: {id: null, interval: 15000, url: ApiUrls.import_progress},
      gridColumns:[
        { title: gettext('File name'), index: false, name: 'file_name'},
        { title: gettext('Start time'), index: false, name: 'start_time'},
        { title: gettext('End time'), index: false, name: 'end_time',
            actions: function(id, attributes) {
                return '<div class="' + 'end-time' + '">' + attributes['end_time'] + '</div>';
            }
        },
        { title: gettext('Status'), index: false, name: 'status',
          actions: function(id, attributes) {
              var className = 'import-pending';
              var status = gettext('Importing..');
              var statusClass = '<i class="fa fa-circle" />';

              if (attributes['status'] == 'success'){
                  className = 'import-success';
                  status = gettext('Successful');
              }else if(attributes['status'] == 'error'){
                  className = 'import-warning';
                  status = gettext('Contains Errors');
              }else{
                  statusClass = '<i class="fa fa-circle" style="display: none"/><span class="task-progress"></span>';
              }

              return '<div class="' + className + '">' + statusClass + ' <span class="task-status">' + status + '</span></div>';
          }
        },
        { title: gettext('Activation File'), index: false, name: 'activation_file',
          actions: function(id, attributes) {
              var display = 'block';
              if (!attributes['activation_file'])
                  display = 'none';

              return '<a style="display:' + display + '" class="activation-file" href="' + attributes['activation_file'] + '"><i class="fa fa-arrow-circle-down" /></a>';

          }
        },
        { title: gettext('Error File'), index: false, name: 'error_file',
          actions: function(id, attributes) {
              var display = 'block';
              if (!attributes['error_file'])
                  display = 'none';

              return '<a style="display:' + display + '" class="error-file" href="' + attributes['error_file'] + '"><i class="fa fa-arrow-circle-down" /></a>';
          }
        },
        { title: gettext('Initiated by'), index: false, name: 'initiated_by'}
      ],
      initialize: function() {
        this.collection.fetch();
      },
      render: function(){
          var _this = this;
          var viewGrid = new bbGrid.View({
            container: this.$el,
            collection: this.collection,
            colModel: _this.gridColumns,
            onBeforeRender: function () {
               // set task_id as row identifier
               _.each(_this.collection.models, function(model){
                    model.cid = model.attributes.task_id;
               });
            },
            onReady: function(){
                // initialize live status update
                _this.initializeProgressCheck();
            }
          });
      },
      initializeProgressCheck: function () {
          var _this = this;

          var options = {
              url: _this.pollingParams.url,
              data: {'progress_check': true},
              type: "GET"
          };
          options.headers = {'X-CSRFToken': $.cookie('apros_csrftoken')};

          $.ajax(options)
              .done(function (data, textStatus, xhr) {
                  if (xhr.status === 200) {
                      // if no in-progress job, then stop status check
                      if (data.length == 0) {
                          clearInterval(_this.pollingParams.id);
                          return;
                      }

                      for (var i in data) {
                          var record = data[i];
                          var status = gettext('Importing..');
                          var recordRow = $('.bbGrid-row[data-cid="' + record.task_id + '"]');

                          if (recordRow.length == 0)
                              continue;

                          if (record.percentage == 100) {
                              recordRow.find('.task-progress').hide();
                              recordRow.find('.task-status').removeClass('in-progress');
                              recordRow.find('.fa-circle').show();

                              recordRow.find('div.end-time').text(record.end_time);

                              if (record.activation_file)
                                  recordRow.find('a.activation-file').attr('href', record.activation_file).show();

                              if (record.error_file) {
                                  recordRow.find('a.error-file').attr('href', record.error_file).show();
                                  recordRow.find('.status div').removeClass('import-pending')
                                      .addClass('import-warning');
                                  status = gettext('Contains Errors');
                              }

                              if (record.activation_file && !record.error_file) {
                                  recordRow.find('.status div').removeClass('import-pending')
                                      .addClass('import-success');
                                  status = gettext('Successful');
                              }
                          } else {
                              status = interpolate(gettext('Importing %(processed)s of %(total)s rows'),
                                  {'processed': record.processed, 'total': record.total}, true);

                              recordRow.find('.task-status').addClass('in-progress');
                              recordRow.find('.task-progress').css({width: record.percentage + '%'})

                          }

                          recordRow.find('.task-status').text(status);

                      }

                      _this.pollingParams.id = setTimeout(
                          _this.initializeProgressCheck.bind(_this),
                          _this.pollingParams.interval
                      );
                  }
              })
              .fail(function (data) {
                  console.log("Ajax failed to fetch data");
                  console.log(data);
              });
      }
  });
 