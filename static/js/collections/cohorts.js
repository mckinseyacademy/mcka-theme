Apros.collections.AdminCohorts = Backbone.PageableCollection.extend({
  initialize: function (options) {
    this.url = ApiUrls.cohorts_list(options.course_id);
  },
  model: Apros.models.Cohort,
  mode: 'client'
});
