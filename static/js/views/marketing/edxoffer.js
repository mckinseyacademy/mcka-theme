Apros.views.Edxoffer = Backbone.View.extend({
  events: {
    'input [data-entry]': 'checkInput',
    'submit #edxoffer': 'edxofferSubmit'
  },

  checkInput: function(e) {
    var entries = this.$('[data-entry]'),
        count = entries.length;
    entries.each(function() {
      var item = $(this);
      if (item.attr('pattern')) {
        var reg = new RegExp(item.attr('pattern'));
        if (reg.test(item.val())) {
          count--;
        }
      } else {
        if (item.val().length) count--;
      }
    });
    this.$('input[type=submit]').prop('disabled', count !== 0);
  },

  edxofferSubmit: function(e) {
    var el = $(e.currentTarget),
        key = el.data('key'),
        entries = $('[data-entry]', el),
        data = {};
    e.preventDefault();

    entries.each(function() {
      var item = $(this);
      data[item.data('entry')] = item.val();
    });

    $.ajax({
      url: 'https://docs.google.com/forms/d/' + key + '/formResponse',
      type: 'POST',
      data: data,
      dataType: 'xml'
    });
    setTimeout(function() {
      $('[data-entry]').val('');
      $('#offer_confirmation').foundation('reveal', 'open');
    }, 300);
  }
});
