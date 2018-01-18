  Apros.views.CourseDetailsEngagementView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch();
    },
    render: function(){
      courseDetailsEngagementViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        colModel:[
        { title: ' ', index: false, name: 'name'},
        { title: gettext('# of people'), index: false, name: 'people' },
        { title: gettext('% total cohort'), index: false, name: 'invited' },
        { title: gettext('Avg Progress'), index: false, name: 'progress' },
        { title: '', index: false, name: '' }
        ]
      });
    }
  });
