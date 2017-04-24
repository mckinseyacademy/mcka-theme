/**
 * Generic util functions
 */



/**
 * Runs HTML escaping and formula injection cleaning on passed properties
 * @param {Object} propObj - properties object
 * @param {Array.<string>} propsToClean - list of properties to apply clean on
 */
Apros.utils.cleanProps = function (propObj, propsToClean) {
    var formulaCleanRegex = Apros.utils.getFormulaCleanRegex();

    _.each(propObj, function(value, prop){
        if(_.contains(propsToClean, prop)){
            value = Apros.utils.escapeHtml(value);

            if(value && Apros.config.ENABLE_FORMULA_CHARACTERS_ESCAPING){
                value = Apros.utils.cleanFormulaInjectionCharacters(value, formulaCleanRegex);
            }

            propObj[prop] = value;
        }
    });

    return propObj;
};


/** Constructs formula clean regex */
Apros.utils.getFormulaCleanRegex = function () {
    var charString = Apros.config.CSV_CHARACTER_BLACKLIST.join('');
    charString = '[' + charString + ']';

    return new RegExp(charString, 'gi');
};


/**
 * Escape HTML entities in string
 * e.g; '<script>' is changed to '&lt;script&gt;'
 */
Apros.utils.escapeHtml = function (string) {
    return _.escape(string);
};


/**
 * Clean formula injection characters from string using passed regex
 * e.g; '=cmd|calc' is changed to 'cmd calc'
 */
Apros.utils.cleanFormulaInjectionCharacters = function (string, regex) {
    if(!regex)
        regex = Apros.utils.getFormulaCleanRegex();

    return string.replace(regex, '');
};
