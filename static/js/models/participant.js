Apros.models.Participant = Backbone.Model.extend({
    parse: function (data, options) {
        return Apros.utils.cleanProps(data, Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN);
    }
});
