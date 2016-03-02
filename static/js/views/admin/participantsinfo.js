Apros.views.ParticipantsInfo = Backbone.View.extend({
	initialize: function(){
		this.collection.fetch();
	},
	render: function(){
		participantsListViewGrid = new bbGrid.View({
			container: this.$el,
			collection: this.collection.fullCollection,
			colModel:[
				{ title: 'Name', index: true, name: 'full_name', 
				actions: function(id, attributes) 
				{ 
					return '<a href="/admin/participants/' + attributes['id'] + '" target="_self">' + attributes['full_name'] + '</a>';
				}},
				{ title: 'Company', index: true, name: 'organizations_custom_name' },
				{ title: 'Email', index: true, name: 'email' },
				{ title: 'Date Added', index: true, name: 'created_custom_date',
				actions: function(id, attributes) 
				{ 
					if (attributes['created_custom_date'] != '-')
					{
						var start = attributes['created_custom_date'].split('/');
						return '' + start[1] + '/' + start[2] + '/' + start[0];
					}
					return attributes['created_custom_date'];
				}},
				{ title: 'Activated', index: true, name: 'active_custom_text' }]
			});
		participantsListViewGrid['partial_collection']=this.collection;
		this.$el.scroll(this.fetchPages);
	},
	fetchPages: function(){
		if  ($(this).find('.bbGrid-container').height() - $(this).height() - $(this).scrollTop() < 20)
		{
			participantsListViewGrid.partial_collection.getNextPage();
		}
	}
});