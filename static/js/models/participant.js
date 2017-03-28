Apros.models.Participant = Backbone.Model.extend({
    parse: function (data, options) {
        return Apros.utils.cleanParticipantProps(data);
    }
});
