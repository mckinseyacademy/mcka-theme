/**
 * Generic util functions
 */

Apros.utils.cleanParticipantProps = function (dataObj) {
    // run clean functions on potentially malicious properties

    _.each(dataObj, function(value, prop){
        if(_.contains(Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN, prop)){
            value = _.escape(value);

            if(value && Apros.config.FORMULA_CHARACTERS_ESCAPING){
                value = Apros.utils.cleanFormulaInjectionCharacters(value);
            }

            dataObj[prop] = value;
        }
    });

    return dataObj;
};


Apros.utils.cleanFormulaInjectionCharacters = function (string) {
    // clean formula injection characters from string

    var charString = Apros.config.CSV_CHARACTER_BLACKLIST.join('');
    charString = '[' + charString + ']';

    var regex = new RegExp(charString, 'gi');

    return string.replace(regex, '');
};
