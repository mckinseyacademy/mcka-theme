  Apros.models.Course_Details = Backbone.Model.extend({
    parse: function (data, options) {
        data.custom_full_name = data.full_name;
        if(data.first_name && data.last_name)
            data.custom_full_name = data.first_name+ " "+ data.last_name;
        return Apros.utils.cleanProps(
            data, 
            _.union(Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN, Apros.config.COMPANY_PROPERTIES_TO_CLEAN)
        );
    }
  });
