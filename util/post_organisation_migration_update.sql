/*
* With the shift from organization group objects to concrete django-model organization objects,
* the data will be migrated within the LMS; however this means that the Apros licensing
* information will be out of date.

This script describes how to manually apply the correct updates; it is as automated as is
practically possible because it is important to have human intervention in case of duplicate matches

*/


/*

1) Map list of old to new groups - with test for multiple matches

NB - Where matches > 1, may need to use SQL in 1a to confirm which matches are which

*/
select auth_group.id as OriginalID, api_manager_organization.id as NewID, COUNT(*) as matches
from api_manager_organization, auth_group
where SUBSTRING(auth_group.name, 7) = api_manager_organization.name GROUP BY api_manager_organization.id;

/* 1a) Script to inform manual pruning of generated script in case of groups with the same name

You may not need this!

*/
select auth_group.id as OriginalID, auth_groupprofile.data, api_manager_organization.*
from api_manager_organization, auth_group, auth_groupprofile
where auth_groupprofile.group_type = "organization"
and auth_groupprofile.group_id = auth_group.id
and SUBSTRING(auth_group.name, 7) = api_manager_organization.name;

/*

2) Generate Apros SQL from results
    e.g. UPDATE `license_licensegrant` set grantor_id=4 WHERE grantor_id = 10;

*/
select concat('UPDATE license_licensegrant set grantor_id = ', api_manager_organization.id, ' where grantor_id = ', auth_group.id, ';') from api_manager_organization, auth_group
where SUBSTRING(auth_group.name, 7) = api_manager_organization.name GROUP BY api_manager_organization.id;

/*

3) Run the Apros SQL on the Apros database

*/