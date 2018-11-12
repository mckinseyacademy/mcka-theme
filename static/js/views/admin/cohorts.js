Apros.views.CohortsUploadCSVView = Backbone.View.extend({
  initialize: function (options) {
    this.course_id = options['course_id'];
    this.template = _.template($('#cohortsUploadTemplate').html());
    this.state = new Backbone.Model();
    this.listenTo(this.state, 'change', this.render);
  },
  events: {
    'change #file-upload-form-file': 'fileSelectionChanged',
    'click #importLearnersBtn': 'submitUsersCSV'
  },

  fileSelectionChanged: function (event) {
    document.getElementById('importLearnersBtn').disabled = event.target.files.length === 0;
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

  render: function () {
    this.$el.html(this.template({
      uploadSuccess: this.state.get('uploadSuccess'),
      uploadError: this.state.get('uploadError'),
      course_id: this.course_id
    }));
  }

});


Apros.views.CohortsDetailView = Backbone.View.extend({
  initialize: function (options) {
    const view = this;
    this.course_id = options['course_id'];
    this.settings = options['settings'];
    this.template = _.template($('#cohortsTemplate').html());
    this.state = new Backbone.Model({
      currentTab: 'add_users',
      selectedCohort: 0,
      userAddResults: null
    });
    this.listenTo(this.settings, 'sync change', this.render);
    this.listenTo(this.state, 'change', this.renderTemplate);
    this.settings.fetch();
    $('button#createCohortBtn').on('click', function () {
      view.createCohort();
    });
    $('a#cancelCreateCohort').on('click', function (event) {
      event.preventDefault();
      $('div#create_cohort').foundation('reveal', 'close');
    });
    this.uploadsView = new Apros.views.CohortsUploadCSVView({
      course_id: this.course_id
    });
  },

  events: {
    'click #cohortCheckbox': 'toggleCohorting',
    'click #addLearnersBtn': 'submitUsers',
    'click #updateCohortBtn': 'updateCohort',
    'change #cohortSelect': 'changeSelectedCohort',
    'click .cohortTabs .tabs .tab': 'changeTab'
  },

  changeTab: function (event) {
    event.preventDefault();
    const element = $(event.currentTarget);
    this.$('.cohortTabs .tabs .tab, .cohortTabs .panels .panel').removeClass('active');
    element.addClass('active');
    $('#' + element.data('panel-id')).addClass('active');
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

  addUsersMessages: function (bucket, count) {
    if (count > 0) {
      switch (bucket) {
        case 'added':
          return ngettext(
            '%s learner has been added to this cohort.',
            '%s learners have been added to this cohort.',
            count
          );
        case 'preassigned':
          return ngettext(
            '%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.',
            '%s learners were preassigned to this cohort. These learners will automatically be added to the cohort when they enroll in the course.',
            count
          );
        case 'changed':
          return ngettext(
            '%s learner has been moved to this cohort.',
            '%s learners have been moved to this cohort.',
            count
          );
        case 'invalid':
          return ngettext(
            '%s invalid email was ignored.',
            '%s invalid emails were ignored.',
            count
          );
        case 'present':
          return ngettext(
            '%s user was already in this cohort.',
            '%s users were already in this cohort.',
            count
          );
        case 'unknown':
          return ngettext(
            '%s user/email was not found.',
            '%s users/email were not found.',
            count
          );
      }
    }
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
          const messages = _(['added', 'preassigned', 'changed', 'invalid', 'present', 'unknown']).map(function (key) {
            const count = result.attributes[key].length;
            const message = view.addUsersMessages(key, count);
            if (message) {
              return {
                label: key,
                message: interpolate(message, [count])
              };
            }
          });
          view.state.set('userAddResults', messages);
          // view.$('div#alertContainer').html(message);
          view.render();
        }
      });
    } else {
      alert('Please add at least one email or username.');
    }
  },

  updateCohort: function () {
    let name = $('input#updateCohortName').val();
    let assignment = $('input[name="cohort-assignment-type"]:checked').val();
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

  learnerCountMessage: function (count) {
    return interpolate(ngettext(
      'contains %s learner',
      'contains %s learners',
      count
    ), [count]);
  },

  renderTemplate: function () {
    this.$el.html(this.template({
      enabled: this.settings.get('is_cohorted'),
      cohorts: this.collection.toJSON(),
      selected: this.state.get('selectedCohort'),
      userAddResults: this.state.get('userAddResults'),
      learnerCountMessage: this.learnerCountMessage,
      course_id: this.course_id
    }));

    // Check current assignment type
    let assignmentRadios = this.$('div.updateCohortAssignment input').toArray();
    let selected = this.collection.at(this.state.get('selectedCohort') || 0);
    assignmentRadios.forEach(function (radio) {
      radio.checked = radio.value === selected.assignment_type();
    });
    this.uploadsView.setElement(this.$('#cohortsUpload')).render();
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
