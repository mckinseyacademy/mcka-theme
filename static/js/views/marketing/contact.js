Apros.views.Contact = Backbone.View.extend({

  events: {
    'submit #tech-support': 'contact_submit'
  },

  contact_submit: function(event) {
    $('[name=device]').val(navigator.platform);
    $('[name=device_language]').val(navigator.language);
    $('[name=browser_type]').val(navigator.vendor);
    $('[name=browser_version]').val(navigator.appVersion);
    $('[name=user_agent]').val(navigator.userAgent);
  }
});
