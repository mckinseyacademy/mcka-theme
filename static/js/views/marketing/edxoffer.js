Apros.views.Edxoffer = Backbone.View.extend({
  events: {
    'submit #edxoffer': 'edxoffer_submit'
  },

  edxoffer_submit: function(event) {
    var el = $(event.currentTarget),
        key = el.data('key'),
        entries = $('[data-entry]', el),
        data = {};
    event.preventDefault();

    entries.each(function() {
      var item = $(this);
      data[item.data('entry')] = item.val();
    });

    $.ajax({
      url: 'https://docs.google.com/forms/d/' + key + '/formResponse',
      type: 'POST',
      data: data,
      dataType: 'xml'
    }).done(function(e){
      console.log(e);
    });
  }
});
