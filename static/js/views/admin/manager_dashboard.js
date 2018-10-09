Apros.views.ManagerDashboardView = Backbone.View.extend({
  managerDashboardReportGridBlock: {},
  generatedGridColumns:
  [
    { title: 'Name', index: true, name: 'custom_full_name', titleAttribute: 'custom_full_name'},
    { title: 'Email', index: true, name: 'email',
      actions: function(id, attributes)
      {
        return '<a href="mailto:' + attributes['email']+'">'+attributes['email'] + '</a>';
      }
    },
    { title: 'Status', index: true, name: 'custom_user_status'},
    { title: 'Activated', index: true, name: 'custom_activated', class: 'status'},
    { title: 'Last Log In', index: true, name: 'custom_last_login',
    actions: function(id, attributes)
    {
      if (attributes['custom_last_login'] != '-' && attributes['custom_last_login'] != '' && typeof attributes['custom_last_login'] != 'undefined')
      {
       var last_login = attributes['custom_last_login'].split(',')[0].split('/');
          return '' + last_login[1] + '/' + last_login[2] + '/' + last_login[0];
      }
      return attributes['custom_last_login'];
    }},
    { title: 'Proficiency', index: true, name: 'proficiency', actions: function(id, attributes)
    {
      value = attributes['proficiency'];
      if (value == '-')
        return value;
      return InternationalizePercentage(parseInt(value));
    }},
    { title: gettext('Progress'), index: true, name: 'progress', actions: function(id, attributes)
    {
      value = attributes['progress'];
      if (value == '-')
        return value;
      return InternationalizePercentage(parseInt(value));
    }},
  ],
  // Delegated events for creating new items, and clearing completed ones.
  events: {
    'click .hashPageButton': 'calculateAverage',
  },
  initialize: function(){
    var _this = this;
    var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
    if (companyPageFlag == 'True')
    {
      var companyId = $('#courseDetailsDataWrapper').attr('company-id');
      this.collection.updateCompanyQuerryParams(companyId);
    }
    this.collection.fetch();
  },
  render: function() {
    managerDashboardReportGridBlock = new bbGrid.View({
      container: this.$el,
      enableSearch: true,
      multisearch: true,
      collection: this.collection,
      colModel: this.generatedGridColumns,
      onReady: function () {
        InitializeAverageCalculate();

        // Activation status icon
        $('#managerDashboardWrapper .status').each(function () {
          if($(this).text().toLowerCase().indexOf("yes") >= 0) {
            $(this).addClass("yes")
          }
          else{
            $(this).addClass("no")
          }
        });
     }
    });
    $('.bbGrid-container').append('<i class="fa fa-spinner fa-spin"></i>');
    managerDashboardReportGridBlock['partial_collection'] = this.collection;
    this.managerDashboardReportGridBlock = managerDashboardReportGridBlock;
    this.$el.find('.bbGrid-container').on('scroll', {extra: this}, this.fetchPages);
    $(document).on('onClearSearchEvent', {extra: this}, this.onClearSearchEvent);
  },
  calculateAverage: function(){
    InitializeAverageCalculate();
  }
});
