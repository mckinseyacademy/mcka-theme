Apros.views.CourseDetailsProblemResponseView = Backbone.View.extend({
  courseBlocksListViewGrid: {},
  initialize: function () {
    var _this = this;
    this.collection.fetch({
      success: function (collection, response, options) {
        _this.render();
      }
    });
  },
  render: function () {
    if (this.collection.length > 0) {
      courseDetailsBlocksViewGrid = new bbGrid.View({
        container: this.$el,
        multiselect: true,
        collection: this.collection,
        enableSearch: true,
        onRowClick: function () {
          $('#downloadResponses').toggleClass('disabled', !this.selectedRows.length);
        },
        colModel: [
          {
            title: gettext('Poll/Survey Question'),
            index: true,
            name: 'question',
            sortType: 'string'
          },
          {
            title: gettext('Lesson'),
            index: true,
            filter: true,
            name: 'lesson',
            sortType: 'string'
          },
          {
            title: gettext('Module'),
            index: true,
            filter: true,
            name: 'module',
            sortType: 'string'
          }
        ]
      });
      this.courseBlocksListViewGrid = courseDetailsBlocksViewGrid;
    } else {
      this.$el.html('No poll/survey questions in this course');
    }
    return this;
  }
});
