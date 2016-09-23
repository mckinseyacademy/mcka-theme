How to enable SSO on a McKinsey/solutions devstack:

# Prerequisites

* Cypress devstack or newer
* Working SAML Identity provider (e.g. testshib.org - more on it later)

# Step 0: Nginx forwarding rules

In production and QA instances, LMS is not directly available - all requests are forwarded via nginx reverse proxy.
Third party auth requests, however, need to get to LMS, so the following nginx rules must be added (if not already
there):

```
server {
    server_name apros.mcka.local;
    # other config settings

    # this rule exists - given here to describe where to place the following rule
    location /api/ {
        try_files $uri @proxy_to_lms_app;
    }

    # this rule needs to be added
    location /auth/ {
        try_files $uri @proxy_to_lms_app;
    }

    # other config settings...

    # this rule already exists, but have different header values set
    location @proxy_to_lms_app {
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $http_host;

        proxy_redirect off;
        proxy_pass http://localhost:8000;
    }
}
```

See [diff][mcka-nginx-docs-diff] for details

[mcka-nginx-docs-diff]: https://github.com/mckinseyacademy/mcka_apros/pull/1189/files#diff-5aec1846a9816293ba7fc9aef3a46686R55

# Step 1: Enable Third Party Auth feature

To enable Third Party Auth feature and configure LMS as SAML Service Provider follow the [official edX guide][tpa-docs]
on enabling third party auth. Caveats:

* Make sure you're actually running Cypress release or newer - edx-platform/common/djangoapps should contain
   `third_party_auth` application.
* If running on solutions fork, make sure [notifications feature conflict][notifications-conflict] is resolved.
  Otherwise, disable the notifications feature in lms.env.json -> FEATURES -> `'ENABLE_NOTIFICATIONS': false`.
* [Exchange Metadata][metadata-exchange] section speaks about exchanging metadata with identity provider: in
  development you might want to use testshib - see the [Testshib Configuration][testshib-configuration] section.
* Identity Provider might not provide a URL LMS can use to fetch metadata, but allows exporting metadata. If that's
  the case, leave "Metadata Source" field empty (if fails validation - set any value). In such case, it is possible to
  set up provider data manually:
  * Go to LMS admin -> Third Party Auth -> Provider Data -> Add new Entry.
  * Fetch Date and Time are irrelevant - set to "Today" and "Now"
  * Expiry Date and Time - set to some arbitrary date in far future (e.g. 5-10 years)
  * Entity Id - get this from metadata file, should be in the `entityId` attribute of `EntityDescriptor` element
    (XPath: //EntityDescriptor[@entityId])
  * SSO URL - leave empty
  * Public key - get this from metadata file - looks like a X509Certificate - a long blob of seemingly random text.
    There might be two of them - you're likely need the one under `IDPSSODescriptor` tag (but that's not verified - so
    far I only had metadata with all certificates equal). XPath: //IDPSSODescriptor//X509Certificate/text()

[tpa-docs]: http://edx.readthedocs.org/projects/edx-installing-configuring-and-running/en/named-release-cypress/configuration/tpa/index.html
[notifications-conflict]: https://openedx.atlassian.net/browse/YONK-148
[metadata-exchange]: http://edx.readthedocs.org/projects/edx-installing-configuring-and-running/en/named-release-cypress/configuration/tpa/tpa_SAML_IdP.html#exchange-metadata
[testshib-configuration]: #testshib-configuration

## Testshib integration

To use testshib as an identity provider, do the following:

1. Configure LMS as Service Provider.
2. Export LMS metadata to a file with a unique name (go to `lms_address/auth/saml/metadata.xml`, save as file)
3. Register the exported metadata with testshib at [Testshib Register page][testshib-register]
4. [Add LMS Identity Provider][lms-add-idp], using testshib [metadata URL][testshib-metadata] as Metadata Source.
5. Set `Email Attribute` to `urn:oid:1.3.6.1.4.1.5923.1.1.1`


[testshib-register]: https://www.testshib.org/register.html
[lms-add-idp]: http://edx.readthedocs.org/projects/edx-installing-configuring-and-running/en/named-release-cypress/configuration/tpa/tpa_SAML_IdP.html#add-and-enable-a-saml-identity-provider
[testshib-metadata]: https://www.testshib.org/metadata/testshib-providers.xml

# Step 2: Enable sharing cookies between LMS and Apros

*(This step is not required on production or if your devstack is configured to access Apros and parts of the LMS using the same domain.)*

By default, LMS sets session cookie at current LMS domain, governed by `SITE_NAME` setting. In order to make LMS session
detection by Apros work, cookies must be shared between LMS and Apros. To do so, edit lms.env.json, so that
`LMS_COOKIE_DOMAIN` contains wildcard that matches both LMS and Apros domains (i.e. if used standard Apros setup,
`.mcka.local` should work just fine)

Then make the corresponding change to Apros in `mcka_apros/local_settings.py`, by adding `LMS_SESSION_COOKIE_DOMAIN = '.mcka.local'`

# Step 3: Wire Apros registration form into LMS third party authentication pilpeline

In `~/lms.auth.json`, configure the LMS to integrate with Apros by adding the following setting. Adjust `mcka.local` to match the domain name you are using for Apros.

```
"THIRD_PARTY_AUTH_CUSTOM_AUTH_FORMS": {
    "apros": {
        "secret_key": "1private_apros_key",
        "url": "http://mcka.local/accounts/finalize/",
        "error_url": "http://mcka.local/accounts/sso_error/"
    }
}
```