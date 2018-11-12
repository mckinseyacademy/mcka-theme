Apros.views.CompanyCustomFieldsView = Backbone.View.extend({
  companyCustomFieldsGridBlock: {},
  generatedGridColumns:
  [
    { title: 'Fields', index: true, name: 'label', titleAttribute: 'label', width: '85%'},
    { title: 'Actions', index: true, name: 'field_action',
        actions: function () {
         return '<i class="fa fa-edit"></i>';
    }
    },
  ],
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
  render: function(){
    companyCustomFieldsGridBlock = new bbGrid.View({
      container: this.$el,
      collection: this.collection,
      colModel: this.generatedGridColumns,
    });
    $('.bbGrid-container').append('<i class="fa fa-spinner fa-spin"></i>');
    companyCustomFieldsGridBlock['partial_collection'] = this.collection;
    this.companyCustomFieldsGridBlock = companyCustomFieldsGridBlock;
    this.$el.find('.bbGrid-container').on('scroll', { extra : this}, this.fetchPages);
}});
