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
  allBlocksSelected: function() {
    return $('#courseBlocksGrid .bbGrid-grid-head-holder input').is(':checked');
  },
  render: function () {
    let _this = this;
    if (this.collection.length > 0) {
      courseDetailsBlocksViewGrid = new bbGrid.View({
        container: this.$el,
        multiselect: true,
        collection: this.collection,
        enableSearch: true,
        onRowClick: function () {
          let selectAllChecked = _this.allBlocksSelected();
          $('#downloadResponsesButton').toggleClass('disabled', !this.selectedRows.length);
          $('#courseBlocksGrid .bbGrid-multiselect-control input').attr('disabled', selectAllChecked);
          if (!selectAllChecked) {
            let unchecked = $('#courseBlocksGrid .bbGrid-multiselect-control input:not(:checked)');
            // If three rows are already checked, disable the rest of the checkboxes
            unchecked.attr('disabled', this.selectedRows.length >= 3);
          }
        },
        colModel: [
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
          },
          {
            title: gettext('Poll/Survey Question'),
            index: true,
            name: 'question',
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
