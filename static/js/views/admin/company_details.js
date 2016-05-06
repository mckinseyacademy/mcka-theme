  Apros.views.CompanyDetailsCoursesView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch();
    },
    render: function(){
      companyDetailsCoursesViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        colModel:[
        { title: 'Course Name', index: true, name: 'name' },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Program', index: true, name: 'program' },
        { title: 'Type', index: true, name: 'type' },
        { title: 'Config.', index: true, name: 'configuration' },
        { title: 'Participants', index: true, name: 'participants' },
        { title: 'Start', index: true, name: 'start' },
        { title: 'End', index: true, name: 'end' },
        { title: 'Cohort Comp.', index: true, name: 'cohort' },
        ]
      });
    }
  });