/**
 * Application-wide variables/configurations
 */


Apros.config.ENABLE_FORMULA_CHARACTERS_ESCAPING = true;

/** Add here any Participant properties that need to be cleaned before rendering */
Apros.config.PARTICIPANT_PROPERTIES_TO_CLEAN = [
    'username',
    'first_name',
    'full_name',
    'title',
    'country',
    'city',
    'custom_full_name',
];

Apros.config.COMPANY_PROPERTIES_TO_CLEAN = [
    'name',
    'organizations_display_name',
    'organizations_custom_name',
];

Apros.config.MOBILEAPP_PROPERTIES_TO_CLEAN = [
    'name'
];

/**
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

// 2-digit to 2-4 digit language code mapping for xblock translations according to edx platform
// Note: Future languages must be mentioned here to work for xblocks
Apros.config.EDX_LANGUAGES_CODE_MAP = new Map([
    ['ar', 'ar'],
    ['de', 'de-de'],
    ['en', 'en'],
    ['es', 'es-419'],
    ['fr', 'fr'],
    ['ja', 'ja-jp'],
    ['nl', 'nl-nl'],
    ['pt', 'pt-br'],
    ['zh', 'zh-cn']
]);
