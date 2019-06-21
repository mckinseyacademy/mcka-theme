Internal SSO Setup Guide
========================

How to Configure SAML SSO for McKinsey Academy Clients.

See [MCKIN-7086](https://edx-wiki.atlassian.net/browse/MCKIN-7086) for background information on this document.

Client setup
------------

1. Send the client our [SSO Playbook](SSO_Client_Setup.md), and review any materials they send us.
   A formatted PDF using McKinsey Academy branding is available, see
   [MCKIN-6968#comment](https://edx-wiki.atlassian.net/browse/MCKIN-6968?focusedCommentId=87101&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-87101).
1. Ensure that their SAML Identity Provider (IdP) meets the requirements.
1. Ask the client to follow the `Integration Procedure` outlined in that document.

Configure SAML service provider on stage
----------------------------------------

### Service Provider Configuration (SAML IdP)

1. Go to https://courses.stage.mckinsey.edx.org/admin/third_party_auth/samlproviderconfig/
1. If an entry for the client already exists, click `Update`. Otherwise, click `Add Provider Configuration (SAML IdP)+`.
1. Set the following. Any setting which isn't mentioned below can be left blank/default.
    * Enabled: True/checked
    * Name: `(Client Name) Stage` (e.g. `Megacorp Inc. Stage`)
    * Visible: `False`
    * Backend name: `tpa-saml`
    * <a name="idp-slug"></a>IdP slug: make one up, short and no spaces, e.g. `megacorp-stage`
    * <a name="entity-id"></a>Entity ID: You can get this from the client's metadata XML. It is usually an attribute on
      the root element in the metadata XML, though in rare cases the metadata XML contains multiple entities and you'll
      have to choose the correct one.
      Example Metadata XML:
      ```xml
      <EntityDescriptor… entityID="https://login-npn-learn.mckinsey.com/saml">
      …
      </EntityDescriptor>
      ```
      Resulting Entity ID: `https://login-npn-learn.mckinsey.com/saml`
    * <a name="metadata-source"></a>Metadata source:
        * If their metadata has a publicly accessible HTTPS URL, put it here. e.g.
          https://stage.sso.megacorp.inc/saml/metadata.xml
        * If their metadata is not accessible via the internet (e.g. they attached it to an email), enter the value
          `https://no-url--must-be-manually-imported/`
    * User ID attribute: Set this to an appropriate value based on the information provided by the client about what
      attributes their IdP is sending. It must be a unique, stable identifier for each user on the IdP.
      Typical values are:
        * `name_id`
          (this will work with most IdPs)
        * `urn:oid:0.9.2342.19200300.100.1.1`
          (this is also the default, so leave the field blank and it will look use this attribute as the user ID)
        * `External Id`
    * Full Name Attribute: Set this to an appropriate value. Typical values are:
        * `Full name`
        * `urn:oid:2.5.4.3` (default)
    * First Name Attribute: Set this to an appropriate value. Typical values are:
        * `Given name`
        * `First Name`
        * `urn:oid:2.5.4.42` (default)
    * Last Name Attribute: Set this to an appropriate value. Typical values are:
        * `Surname`
        * `Last Name`
        * `urn:oid:2.5.4.4` (default)
    * Username Hint Attribute: Set this to an appropriate value. Typical values are:
        * `Username`
        * `Given name`
        * `urn:oid:0.9.2342.19200300.100.1.1` (default)
    * Email Attribute: Set this to an appropriate value. Typical values are:
        * `Email`
        * `urn:oid:0.9.2342.19200300.100.1.3`
    * Debug Mode: True
1. Save changes.

### Verify service provider

Check that the metadata was retrieved successfully for the new SP:

1. Go to https://courses.stage.mckinsey.edx.org/admin/third_party_auth/samlproviderdata/
1. Look for the metadata of the new provider (if it's not there, see below).
1. Make sure it has a green `Is Valid` checkmark.

If the [metadata did not have a publicly accessible URL](#metadata-source), you will have to add it manually here:

1. Click `Add SAML Provider Data +`
1. Set `Fetched At` to the current date/time
1. Set `Expires At` to a date at least ten years in the future
1. Get the `SSO URL` from their metadata. It's the `Location` attribute of the element that specifies the
   SingleSignOnService with the redirect binding, e.g.:
   ```xml
   <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                       Location="https://stage.sso.megacorp.inc/saml/redirect/sso" />
   ```
1. Get the public key from the metadata. It will be a long text value like `MIIC4jCCAcqgAwIBAgICBu4wDQYJK...` and will
   be in the `<KeyDescriptor><*:KeyInfo><*:X509Data><*:X509Certificate>` element, where the `*` part varies).
1. Save.

### Set up MCKA Apros Client SSO

Link the IdP to the Client in MCKA ADMIN:

1. Go to https://stage.mckinsey.edx.org/admin/clients/
1. Find the client in the list, and click its name to view the client details.
1. Click the `SSO` tab at the top.
1. Set the `Identity provider` value to the [Idp slug](#idp-slug) value set in the SAML provider config.
1. Click `Save`.

Create an Access Key for the test:

1. From the above client SSO page, click `Create Course Access Key`, or use an existing one.
1. Click on `Share` to copy access key's URL, e.g.

        https://stage.mckinsey.edx.org/access/349e6bd1-217c-4cc7-838e-883e17af5870

Test that the Access Key seems to work:

1. Open the access key URL copied above in an incognito window.
1. Verify that you get redirected to the login provider.
   If you don't, check all prior steps or see the LMS and/or Apros logs on Splunk for a detailed error message, and
   review [Troubleshooting](#troubleshooting) below.
1. That is likely as far as we can test without the client's help.

Send the stage access key to the client:
1. Ask them to click on it while sharing their screen with us.
1. If an error occurs, get the error details from the LMS logs on Splunk, and review [Troubleshooting](#troubleshooting)
   below.

Success! Now we need to disable `Debug Mode` for security reasons.

1. Go to https://courses.stage.mckinsey.edx.org/admin/third_party_auth/samlproviderconfig/
1. Click on the `Update` link to the right of the provider in question (it will show `Debug mode` in red).
1. Set `Debug mode` to false (unchecked) and save changes.

Configure SAML service provider on production
---------------------------------------------

When ready: repeat the [above procedure](#configure-saml-service-provider-on-stage) on Prod, instead of Stage.  Use the
client's metadata and other info for their production IdP, not their stage IdP.

For security reasons, ensure that the `Debug mode` flag is false (unchecked) unless you're actively debugging the setup.

Relevant URLs are:
* https://courses.mckinseyacademy.com/admin/third_party_auth/samlproviderconfig/
* https://courses.mckinseyacademy.com/admin/third_party_auth/samlproviderdata/
* https://www.mckinseyacademy.com/admin/clients/


Update ceritficate for SAML Provider
------------------------------------

Sometimes a client will change the certificate they use for SAML and we will
need to update the certificate in our configuration as well. This is a pretty
simple process.

If a publicly-available SAML metadata url was set up during the initial process,
this will happen automatically at some point as the metadata is regularly
refreshed.

However, in many cases the certificate has been manually configured in a new
`SAML Provider Data` instance. In that case you can simply repeat the process
in the [Verify service provider](#Verify-service-provider) section above for
setting up metadata when a URL isn't provided. Note that you can't modify the
existing entry, and you don't need to delete it either. The latest entry will
automatically be used, and it's good to have a record of certificate changes.

Troubleshooting
---------------

First, make sure we sent the client the right SP metadata URLs. There are (at least) two URLs for each metadata file,
but only one will work:

* https://stage.mckinsey.edx.org/auth/saml/metadata.xml - correct :white_check_mark:
* <strike>https://courses.stage.mckinsey.edx.org/auth/saml/metadata.xml</strike> - WRONG :x:
* https://www.mckinseyacademy.com/auth/saml/metadata.xml - correct :white_check_mark:
* <strike>https://courses.mckinseyacademy.com/auth/saml/metadata.xml</strike> - WRONG :x:

Other common issues are below. For most of these issues, the end user will just see a generic SSO error message. You
must access the LMS logs in Splunk or New Relic to get the actual error (while `Debug Mode` is enabled for the IdP).  To
retrieve the logs from Splunk, use a query like the following (change `megacorp` to the client's name, and change the
dates to an appropriate window):

```
'index=stage-mckinsey earliest=03/06/2018:21:30:00 latest=3/06/2018:23:00:00 (SAML OR megacorp)'
```

If the Splunk log contains no useful information, also check New Relic (`edxapp-lms`) for an error message.

### <StatusMessage>The AuthnRequest with AuthnContexts is not supported!</StatusMessage>

The reason is that our python-saml SP is sending an AuthnRequest that requires the IdP to authenticate users using
`PasswordProtectedTransport`, but the IdP refuses to use that form of authentication. A fix is explained in this
[openedx-ops post](https://groups.google.com/d/msg/openedx-ops/d-rmACND180/kNgcxHlmIAAJ), though it should already be
applied on McKA stage and prod, so you are unlikely to encounter this issue again.

### Authentication failed: SAML login failed: ['invalid_response'] (Invalid issuer in the Assertion/Response)

The Issuer entity ID in the IdP's response does not match the Entity ID in the metadata that they sent us (configured
[above](#entity-id)).  Ask them to fix it; you may need to update the `Provider Configuration (SAML IdP)` and/or `SAML
Provider Data` Entity ID values on our side too, if they are changed or wrong.

### exceptions:KeyError: 'urn:oid:0.9.2342.19200300.100.1.1' in /social.apps.django_app.views:complete

Our SP is looking for an attribute that their provider did not send.

Go to the [Provider Configuration (SAML IdP)](#service-provider-configuration-saml-idp) section, click on the `Update`
link to the right of the provider in question, and fix whichever attribute (e.g. `User ID attribute`) is causing the
problem.

In the above example, the default user ID (`urn:oid:0.9.2342.19200300.100.1.1`) was not one of the attributes that the
IdP sent, so we had to change the user ID attribute to `name_id`.

The Splunk logs should contain a complete list of all the attributes the IdP sent, though they'll be in XML format.

### IndexError: list index out of range in social/backends/saml.py, in get_attr

Their IdP is including an attribute that we need, but it has no value. We ran into this once when a client was testing
with a test user account that had no `Last name`. Tell the client to test with a real user account, or make sure their
test user has all required attributes.

### More

Some other troubleshooting information is available in [SSO Devstack setup](SSO_Devstack_Setup.md#troubleshooting).
