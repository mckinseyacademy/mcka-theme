Apros.views.CohortsDetailView = Backbone.View.extend({
  initialize: function (options) {
    this.course_id = options['course_id'];
    this.settings = options['settings'];
    this.template = _.template($('#cohortsTemplate').html());
    this.state = new Backbone.Model({
      selectedCohort: 0
    });
    this.listenTo(this.settings, 'sync change', this.render);
    this.listenTo(this.state, 'change', this.renderTemplate);
    this.settings.fetch();
    $('button#createCohortBtn').on('click', function () {
      view.createCohort();
    });
  },
  events: {
    'click #cohortCheckbox': 'toggleCohorting',
    'click #addLearnersBtn': 'submitUsers',
    'click #updateCohortBtn': 'updateCohort',
    'change #cohortSelect': 'changeSelectedCohort',
    'change #file-upload-form-file': 'fileSelectionChanged',
    'click #importLearnersBtn': 'submitUsersCSV'
  },

  fileSelectionChanged: function (event) {
    document.getElementById('importLearnersBtn').disabled = event.target.files.length === 0;
  },

  createCohort: function () {
    let name = $('input#newCohortName').val();
    let assignment;
    for (let radio of $('div.newCohortAssignment input').toArray()) {
      if (radio.checked) {
        assignment = radio.value;
        break;
      }
    }
    let view = this;
    let model = new Apros.models.Cohort({course_id: this.course_id});
    model.save({name: name, assignment_type: assignment}, {
      headers: {'X-CSRFToken': $.cookie('apros_csrftoken')},
      patch: true,
      success: function (result) {
        $('div#create_cohort').foundation('reveal', 'close');
        view.render();
      }
    });
  },

  toggleCohorting: function () {
    this.settings.save(
      {is_cohorted: !this.settings.get('is_cohorted')},
      {headers: {'X-CSRFToken': $.cookie('apros_csrftoken')}});
  },

  submitUsers: function () {
    let form = this.$('#addUsersForm');
    let view = this;
    if (form.val()) {
      let cohort = this.collection.toJSON()[this.state.get('selectedCohort') || 0];
      let users = new Apros.models.AdminCohortUsers({course_id: this.course_id, cohort_id: cohort.id});
      let payload = {users: form.val().split(/[ ,\n]/)};
      users.save(payload, {
        headers: {'X-CSRFToken': $.cookie('apros_csrftoken')},
        success: function (result) {
          let message = '<hr/>';
          result = result.attributes;

          if (result.added.length) {
            message += '<p>' + result.added.length + ' learners added to this cohort.</p>';
          }
          if (result.changed.length) {
            message += '<p>' + result.changed.length + ' learners moved to this cohort.</p>';
          }
          if (result.invalid.length) {
            message += '<p>' + result.invalid.length + ' invalid emails where ignored.</p>';
          }
          if (result.present.length) {
            message += '<p>' + result.present.length + ' learners already present in the cohort.</p>';
          }
          if (result.unknown.length) {
            message += '<p>' + result.unknown.length + ' user/emails not found.</p>';
          }
          view.$('div#alertContainer').html(message);
        }
      });
    } else {
      alert('Please add at least one email or username.');
    }
  },

  updateCohort: function () {
    let name = $('input#updateCohortName').val();
    let assignment;
    for (let radio of $('div.updateCohortAssignment input').toArray()) {
      if (radio.checked) {
        assignment = radio.value;
        break;
      }
    }
    let view = this;
    let model = this.collection.at(this.state.get('selectedCohort') || 0);
    model.save({
      name: name, assignment_type: assignment
    }, {
      headers: {'X-CSRFToken': $.cookie('apros_csrftoken')},
      success: function (result) {
        view.render();
      },
      url: ApiUrls.cohort_handler(this.course_id, model.id)
    });
  },

  changeSelectedCohort: function (event) {
    this.state.set('selectedCohort', event.currentTarget.value);
  },

  setUploadError: function (message) {
    this.state.set({
      uploadSuccess: false,
      uploadError: message
    });
  },

  submitUsersCSV: function (event) {
    event.preventDefault();
    const view = this;
    const form = $('#file-upload-form');
    form.ajaxSubmit({
      error: function () {
        view.setUploadError(gettext('There was an error submitting your file.'));
      },
      success: function (data) {
        if (data.error_code) {
          if (data.error_code === 'failed-validation') {
            view.setUploadError(gettext('Invalid format for CSV file.'));
          } else {
            view.setUploadError(gettext('Error processing CSV file.'));
          }
        } else {
          view.state.set({uploadSuccess: true, uploadError: null});
        }
      }
    });
    this.renderTemplate();
  },

  renderTemplate: function () {
    this.$el.html(this.template({
      enabled: this.settings.get('is_cohorted'),
      cohorts: this.collection.toJSON(),
      selected: this.state.get('selectedCohort'),
      uploadSuccess: this.state.get('uploadSuccess'),
      uploadError: this.state.get('uploadError'),
      course_id: this.course_id
    }));

    // Check current assignment type
    let assignmentRadios = this.$('div.updateCohortAssignment input').toArray();
    let selected = this.collection.at(this.state.get('selectedCohort') || 0);
    assignmentRadios.forEach(function (radio) {
      radio.checked = radio.value === selected.assignment_type();
    });
  },

  render: function () {
    let view = this;
    if (this.settings.is_cohorted() && !this.fetchingCollection) {
      this.fetchingCollection = true;
      this.collection.fetch({
        success: function () {
          view.fetchingCollection = false;
          view.renderTemplate();
        }
      });
    }
    view.renderTemplate();
  }

});
