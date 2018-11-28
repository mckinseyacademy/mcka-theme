Apros.views.ManagerDashboardView = Backbone.View.extend({
  managerDashboardReportGridBlock: {},
  generatedGridColumns:
  [
    { title: 'Name', index: true, name: 'custom_full_name', titleAttribute: 'custom_full_name'},
    { title: 'Email', index: true, name: 'email',
      actions: function(id, attributes)
      {
        return '<a id="email" href="mailto:' + attributes['email']+'">'+attributes['email'] + '</a>';
      }
    },
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
        return '<span>'+InternationalizePercentage(parseInt(value))+'</span>' + '<a href="JavaScript:Void(0)" class="toggle-subgrid show-subgrid button tiny" data-title="'+attributes["username"]+'">View Details</a>';
    }},

  ],
  // Delegated events for creating new items, and clearing completed ones.
  events: {
    'click .show-subgrid': 'showSubGrid',
    'click .bbGrid-row': 'hideSubGrid',
    'click .hide-subgrid': 'hideSubGrid',
    'click .hashPageButton': 'calculateAverage',
  },
  buttonClicked: false,
  initialize: function() {
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
      enableSearch: false,
      multisearch: false,
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
    this.$el.find('.bbGrid-container').on('scroll', { extra : this}, this.fetchPages);
    $(document).on('onClearSearchEvent', { extra : this}, this.onClearSearchEvent);
  },
  showSubGrid: function(e) {
    var element = $(e.target);
    RemoveExistingSubGird(element);
    var parentElement = $(element).parent().parent();
    var index = $(parentElement).attr('data-cid');
    var course_id = $("a.hashPageButton.active").attr('data-course');
    var username = $(element).attr("data-title");
    var url = "student_report/"+username+"/course/"+course_id;
    Backbone.ajax({
      dataType: "json",
      url: url,
      data: "",
      success: function (val) {
        var container = "";
        $.each( val, function( key, value ){
          container += '<tr class="bbGrid-row bbSubGrid subgrid-' + index + '" data-parent-cid="'+index+'"><td></td><td colspan="4">'+gettext("Lesson")+' '+parseInt(key + 1)+': '+value.name+'</td><td colspan="3"> '+value.progress+'% '+gettext("complete")+'</td></tr>';
        });
        $(container).insertAfter(parentElement);
      },
      fail: function(error){
        alert(gettext("Error Occured!"));
      }
    });
    $(element).text(gettext('Hide Details'));
    $(element).removeClass('show-subgrid');
    $(element).addClass('hide-subgrid');
    this.buttonClicked = true;
  },
  hideSubGrid: function(e) {
    var element = $(e.target);
    var tagName = $(element).prop('tagName');
      if(this.buttonClicked) {
        this.buttonClicked = false;
        return;
      }

      if(tagName == "A") {
        // if clicked on other anchor tags like email, course tabs
        if(!$(element).hasClass("toggle-subgrid")){
          RemoveExistingSubGird(element);
          return;
        }
      }
      else {
        var parentElement = $("[class*='bbSubGrid']")[0];
        var data_cid = $(parentElement).attr('data-parent-cid');
        element = $("a.toggle-subgrid", "tr[data-cid='"+data_cid+"']");

      }

    $("tr.bbSubGrid").each(function() {
      $(this).remove();
    });
    $(element).text(gettext('View Details'));
    $(element).removeClass('hide-subgrid');
    $(element).addClass('show-subgrid');
  },
  calculateAverage: function() {
    InitializeAverageCalculate();
  }
});
