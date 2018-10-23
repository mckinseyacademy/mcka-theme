Apros.models.Cohort = Backbone.Model.extend({
  idAttribute: 'id',
  initialize: function (options) {
    this.urlRoot = ApiUrls.cohorts_list(options['course_id']);
  },
  user_count: function () {
    return this.get('user_count');
  },
  name: function () {
    return this.get('name');
  },
  assignment_type: function () {
    return this.get('assignment_type');
  },
  group_id: function () {
    return this.get('group_id');
  },
  user_partition_id: function () {
    return this.get('user_partition_id');
  }
});

Apros.models.AdminCohortSettings = Backbone.Model.extend({
  initialize: function (options) {
    this.url = ApiUrls.cohorts_settings(options['course_id']);
  },
  is_cohorted: function () {
    return this.get('is_cohorted');
  }
});

Apros.models.AdminCohortUsers = Backbone.Model.extend({
  initialize: function (options) {
    this.url = ApiUrls.cohorts_users(options['course_id'], options['cohort_id']);
  },
  default: {
    users: []
  }
});
