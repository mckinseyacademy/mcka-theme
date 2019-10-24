# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20170320_0716'),
    ]

    # On prod and stage `accounts_remoteuser_groups` and `accounts_remoteuser_user_permissions` do not 
    # exist while they should have been there because initial migration of accounts app is creating them.
    # Though these tables do exists on QA and local development environments. To tackle this
    # inconsistency we are adding this migration to create these table only if they do not exist.
    operations = [
	    migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS accounts_remoteuser_groups (
              id int(11) NOT NULL AUTO_INCREMENT,
              remoteuser_id int(11) NOT NULL,
              group_id int(11) NOT NULL,
              PRIMARY KEY (id),
              UNIQUE KEY remoteuser_id (remoteuser_id,group_id),
              KEY accounts_remoteuser_g_group_id_30d378215bc5987b_fk_auth_group_id (group_id),
              CONSTRAINT account_remoteuser_id_177fa61e42ba62e2_fk_accounts_remoteuser_id FOREIGN KEY (remoteuser_id) REFERENCES accounts_remoteuser (id),
              CONSTRAINT accounts_remoteuser_g_group_id_30d378215bc5987b_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES auth_group (id)
            )
            """
        ),
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS accounts_remoteuser_user_permissions (
              id int(11) NOT NULL AUTO_INCREMENT,
              remoteuser_id int(11) NOT NULL,
              permission_id int(11) NOT NULL,
              PRIMARY KEY (id),
              UNIQUE KEY remoteuser_id (remoteuser_id,permission_id),
              KEY accounts_re_permission_id_4f3997655c8762d6_fk_auth_permission_id (permission_id),
              CONSTRAINT account_remoteuser_id_2625dd0145921490_fk_accounts_remoteuser_id FOREIGN KEY (remoteuser_id) REFERENCES accounts_remoteuser (id),
              CONSTRAINT accounts_re_permission_id_4f3997655c8762d6_fk_auth_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
            )
            """
        ),
    ]
