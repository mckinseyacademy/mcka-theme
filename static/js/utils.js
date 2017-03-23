/**
 * Generic util functions
 */

Apros.utils.cleanParticipantProps = function (modelInstance, dataObj) {
    // run escape on potentially malicious properties
    _.each(dataObj, function(value, prop){
        if(_.contains(Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN, prop)){
            dataObj[prop] = modelInstance.escape(prop);
        }
    });

    return dataObj;        
};
