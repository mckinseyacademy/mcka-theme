Apros.models.Participant = Backbone.Model.extend({
    parse: function (data, options) {
        options.parse = false; // Important: otherwise will produce endless recursion

        // creating a `dummy` record just to use `escape` functionality of backbone models
        var record = new this.collection.model(data, options);

        return Apros.utils.cleanParticipantProps(record, data);
    }
});
