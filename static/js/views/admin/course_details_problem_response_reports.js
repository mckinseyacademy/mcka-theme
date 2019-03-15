Apros.views.CourseDetailsProblemResponseReportsView = Backbone.View.extend({
  problemResponseReportsListViewGrid: {},
  rendered: false,
  render: function () {
    if (!this.rendered) {
      problemResponseReportsViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        enableSearch: false,
        colModel: [
          {
            title: gettext('Filename'), index: false, name: 'name', actions: function (id, attributes) {
              if (attributes.status === 'DONE') {
                return _.template('<a href="<%= url %>"><%- name %></a>', attributes);
              } else if (attributes.status === 'PROGRESS') {
                this.$el.addClass('report-pending');
                return _.template('<span class="report-pending">Pending report for <%- problem_location %></span>',
                  attributes.parameters);
              } else if (attributes.status === 'ERROR') {
                this.$el.addClass('report-error');
                return _.template('<span class="report-error">Error processing report for <%- problem_location %></span>',
                  attributes.parameters);
              } else if (attributes.name) {
                return attributes.name;
              }
              return _.template('Report for <%- problem_location %>', attributes.parameters);
            }
          },
          {
            title: gettext('Request Time'),
            index: false,
            name: 'requested_datetime',
            actions: function (id, attributes) {
              return moment(attributes['requested_datetime']).fromNow();
            }
          }
        ]
      });
      $('.bbGrid-container').append('<i class="fa fa-spinner fa-spin"></i>');
      this.problemResponseReportsListViewGrid = problemResponseReportsViewGrid;
      this.rendered = true;
    }
    return this;
  }
});
