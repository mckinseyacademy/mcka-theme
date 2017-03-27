/*

Application-wide variables/configurations  

 */


Apros.config.FORMULA_CHARACTERS_ESCAPING = true;

// Add here any Participant properties that need to be cleaned before rendering
Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN = [
    'username',
    'first_name',
    'full_name',
    'title',
    'country',
    'city'
];


/*
Add here any characters that should not be present in CSV exports
Note: If a character needs escaping in regex, give escaping along with the character e.g; '-' is written as '\\-'
*/
Apros.config.CSV_CHARACTER_BLACKLIST = [
    '+',
    '\\-',
    '=',
    '|',
    '!',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '(',
    ')',
    ':',
    ';',
    '*'
];
