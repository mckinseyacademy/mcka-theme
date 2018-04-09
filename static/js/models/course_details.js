  Apros.models.Course_Details = Backbone.Model.extend({
    parse: function (data, options) {
        return Apros.utils.cleanProps(
            data, 
            _.union(Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN, Apros.config.COMPANY_PROPERTIES_TO_CLEAN)
        );
    }
  });
