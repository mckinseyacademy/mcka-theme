  Apros.models.Company = Backbone.Model.extend({
      parse: function (data, options) {
        return Apros.utils.cleanProps(data, Apros.config.COMPANY_PROPERTIES_TO_CLEAN);
      }
  });
  