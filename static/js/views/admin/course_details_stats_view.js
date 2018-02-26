  Apros.views.CourseDetailsStatsView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch();
    },
    render: function(){
      courseDetailsStatsViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        colModel:[
        { title: ' ', index: false, name: 'name'},
        { title: '#', index: false, name: 'value' },
        ]
      });
    }
  });