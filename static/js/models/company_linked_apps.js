 Apros.models.CompanyLinkedApps = Backbone.Model.extend({
    parse: function (data, options) {
        return Apros.utils.cleanProps(data, Apros.config.MOBILEAPP_PROPERTIES_TO_CLEAN);
    }
  });
