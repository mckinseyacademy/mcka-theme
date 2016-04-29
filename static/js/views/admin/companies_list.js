  Apros.views.CompaniesListView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch({success: function(collection, response, options){
        cloneHeader('#companiesListViewGridBlock');
        collection.getSlowFetchedStatus = true;
        collection.slowFieldsSuccess(collection, response, options);
      }});
    },
    render: function(){
      companiesListViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        enableSearch: true,
        colModel:[
        { title: 'Company', index: true, name: 'name',
          actions: function(id, attributes){ 
            var thisId = attributes['id']
            var name = attributes['name']
            if (name)
              return '<a href="/admin/clients/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: 'Company ID', index: true, name: 'id', sorttype: 'number' },
        { title: 'No. of Participants', index: true, name: 'numberParticipants', sorttype: 'number',
          actions: function(id, attributes){ 
            var numberParticipants = attributes['numberParticipants']
            if (numberParticipants == '.') {
              return '<i class="fa fa-spinner fa-spin"></i>';
            }
            else{
              return numberParticipants;
            }
          } 
        },
        { title: 'No. of Courses', index: true, name: 'numberCourses' }
        ]
      });
      this.companiesListViewGrid = companiesListViewGrid;
      $(document).on('onClearSearchEvent', { extra : this}, this.onClearSearchEvent);
    },
    onClearSearchEvent: function(event){
      var _this = event.data.extra;
      _this.companiesListViewGrid.searchBar.onSearch({target: '#mainCompaniesListGridWrapper .bbGrid-pager'});
    },
  });