/**
 * Generic util functions
 */

Apros.utils.cleanParticipantProps = function (dataObj) {
    // run clean functions on potentially malicious properties

    var formulaCleanRegex = Apros.utils.getFormulaCleanRegex();

    _.each(dataObj, function(value, prop){
        if(_.contains(Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN, prop)){
            value = Apros.utils.escapeHtml(value);

            if(value && Apros.config.FORMULA_CHARACTERS_ESCAPING){
                value = Apros.utils.cleanFormulaInjectionCharacters(value, formulaCleanRegex);
            }

            dataObj[prop] = value;
        }
    });

    return dataObj;
};


Apros.utils.getFormulaCleanRegex = function () {
    // construct formula clean regex

    var charString = Apros.config.CSV_CHARACTER_BLACKLIST.join('');
    charString = '[' + charString + ']';

    return new RegExp(charString, 'gi');
};


Apros.utils.escapeHtml = function (string) {
    // escape HTML entities in string
    // e.g; '<script>' is changed to '&lt;script&gt;'

    return _.escape(string);
};


Apros.utils.cleanFormulaInjectionCharacters = function (string, regex) {
    // clean formula injection characters from string using passed regex
    // e.g; 'cmd|calc' is changed to 'cmd calc'

    if(!regex)
        regex = Apros.utils.getFormulaCleanRegex();

    return string.replace(regex, '');
};
