# Using saml-idp for local SAML testing

It is possible to run your own local IdP server that can be inspected and configured with greater ease.

One such simple solution is [saml-idp](https://github.com/mcguinness/saml-idp), an open source Node-based IdP server that is designed for testing. It has no concept of users accounts. Instead, you can fill in whatever details you'd like for parameters like "First Name", "Last Name", "Display Name", "E-Mail Address" etc. You can even add custom parameters, or remove existing parameters via a config file and GUI.

This allows you to quickly test the registration flow by simply signing in using this IdP and filling in new details. You can log in to an existing account with just a matching username and email.

## Setting up saml-idp

The easiest way to get `saml-idp` is to install it using `npm install --global saml-idp`. It is also possible to run it in Docker using the provided Docker config in the [repository for saml-idp](https://github.com/mcguinness/saml-idp). Follow the instructions given in the repository to set up `saml-idp`.

By default `saml-idp` will launch the server on port 7000 and advertise itself on ``http://<your-hostname>:7000/``. This works great outside the devstack, however, your hostname will probably not resolve correctly inside the devstack.

The IdP will need to be accessible both inside and outside the devstack, so the easiest solution is to modify the hosts file inside the devstack to point to the IP of your host machine. From within the devstack VM, your host machine should be accessible on `192.168.33.01`. So add an entry to the devstack's hosts file that resolves the hostname of your host machine to this IP address. You can find out more about how to locate and edit this file in its [manual](http://man7.org/linux/man-pages/man5/hosts.5.html).

## Configuring saml-idp

After you've set up `saml-idp` using the instructions in the repository's readme, you can launch it with a few config options that are explained here:

* `--issuer`: The issuer ID. You will need to fill this in as the "Entity ID".
* `--audience`: This is the entity ID for the LMS as a service provider. Enter the value filled in when creating a config [here](http://lms.mcka.local/admin/third_party_auth/samlconfiguration/).
* `--acs`: Fill in `http://apros.mcka.local/auth/complete/tpa-saml/`

Now you can launch the app as:

    saml-idp --issuer my:saml:idp --audience sp-entity-id --acs http://apros.mcka.local/auth/complete/tpa-saml/

At this point, you can open the [admin page for adding a new SAML IdP](http://lms.mcka.local/admin/third_party_auth/samlproviderconfig/add/). Some of the settings you need to fill in here can be provided as command line options to `saml-idp`.

Here is what you need to fill in on this page:

* Enabled: checked
* Name: Fill in any friendly name, like "My Local IdP"
* Visible: checked
* Idp slug: Fill in a unique slug for this provider, like "local-idp"
* Entity ID: Fill in the string you provided for `--issuer`
* Metadata source: `http://<local-host-name>:7000/metadata`
  Note that this URL should be accessible to the LMS running inside the devstack VM, so it can't be localhost or a local IP.
* User ID Attribute: name_id
* Full Name Attribute: displayName
* First Name Attribute: firstName
* Last Name Attribute: lastName
* Username Hint Attribute: displayName
* Email Attribute: email

All other options may be left to their defaults.

At this point, you can proceed with the rest of the steps of the IdP configuration, such as pulling in the latest metadata using `python manage.py lms saml --pull --settings=devstack`.
