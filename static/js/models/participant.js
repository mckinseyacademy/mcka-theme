Apros.models.Participant = Backbone.Model.extend({
    parse: function (data, options) {
        options.parse = false; // Important: otherwise will produce endless recursion

        // creating a `dummy` record just to use `escape` functionality of backbone models
        var record = new this.collection.model(data, options);

        // run escape on potentially malicious properties
        _.each(data, function(value, prop){
            if(_.contains(Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN, prop)){
                data[prop] = record.escape(prop);
            }
        });

        return data;
    }
});