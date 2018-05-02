Mobile SSO Setup Guide
=========================

How set up Mobile SSO for the Android/iOS apps.

Single Sign On from the McKinsey Academy mobile apps works using a combination of OAuth2 and SAML configuration.

Overview
--------

When a user enters a username or email into the app login screen, the app will use the Solutions
LMS's `<LMS>/api/third_party_auth/v0/users/<identifier>` URL to retrieve the IdP associated with that
login ID.  (If no IdPs are returned by the API, then a password field should be shown, and
authentication for that login ID proceeds without SSO.)

The app will then open the Apros `sso_launch` URL with the IdP `provider_id` and the configured
`mobile_url_scheme` in a web view or web browser.  That endpoint will start the SAML auth flow, and
if SSO authentication is successful, will redirect to the Apros `sso_finalize` URL.  If the OAuth2
client is marked as "trusted", then this will automatically forward the SSO authenticated user back
to the app, using the `mobile_url_scheme`.

For example, if the `mobile_url_scheme` is `mcka`, the final URL will be either
`mcka://sso/?access_token=...` or `mcka://sso/?error=...` if there is an error.

Which URLs to use?
------------------

This guide references URLs for both the LMS and Apros.  Take care to use the URLs appropriate to your environment:

### Devstack

* LMS: http://lms.mckin.local
* Apros: http://apros.mckin.local

### Stage

* LMS: https://courses.stage.mckinsey.edx.org
* Apros: https://stage.mckinsey.edx.org

### Production

* LMS: https://courses.mckinseyacademy.com
* Apros: https://www.mckinseyacademy.com

Step 1. Set up SSO
------------------

This needs to be done for each client's SSO.

See [Internal SSO Setup Guide](SSO_Internal_Setup.md) for how to configure a SAML SSO for a client.

Step 2. Set up OAuth2
---------------------

This only needs to be done once, to allow Apros to authenticate to the LMS on behalf of the mobile app.

1.  Set `ALLOW_UNPRIVILEGED_SSO_PROVIDER_QUERY: true` in `lms.env.json`.
1.  Create a new OAuth client at `<LMS>/admin/oauth2_provider/application/`
1.  For the user pick or create a staff user account that is dedicated for the purpose.
1.  In the "Redirect uris" box put in `<Apros>/accounts/finalize/`
1.  For "Client type" select "Confidential"
1.  For "Authorization grant type" select "Authorization code"
1.  Note the client id and secret, and ensure they are saved to the Apros Stage settings
    `OAUTH2_MOBILE_CLIENT_ID` and `OAUTH2_MOBILE_CLIENT_SECRET`, respectively.
    *Important* `OAUTH2_MOBILE_CLIENT_ID` must be a unique OAuth2 client identifier.
1.  Enable "Skip authorization". This step can be skipped if you want SSO-authenticated users to
    explicitly grant permission for the mobile application to use their authenticated session.

Mobile app SSO login
--------------------

1.  Set up a mobile URL scheme for the app, which will redirect mobile browser links prefixed with
    that scheme back to the mobile app.  The scheme may contain alphanumeric characters or hypens,
    no underscores.  For example, `mckin`.
1.  Ensure that the mobile app responds to the `/sso` endpoint.  Expected parameters are:
    *   `access_token`: Indicates successful authentication.  This token may be used for LMS or
        Apros API calls.
    *   `error`: Indicates an error in the SSO pipeline.
1.  On the login screen, request the user's `username` or `email`, also known as the "login
    identifier", or Login ID.
1.  Post the Login ID to `<LMS>/third_party_auth/api/v0/users/<identifier>` endpoint, to fetch the
    list of SSO providers available for that user.  Example return data for a Login ID
    `someone@megacorp.com`:

    ```javascript
    {
        "active": [
            {
                "provider_id": "saml-megacorp",
                "name": "Megacorp Inc."
            },
            ...
        ]
    }
    ```
1.  Use the (first) returned `provider_id` and the mobile app URL scheme from Step 1 to start the
    SSO login flow in a web view or web browser with this URL:
    `<Apros>/accounts/sso_launch/?provider_id=<provider_id>&mobile_url_scheme=<mobile_scheme>`
1.  The user will follow the SSO flow to login to their SSO.  Once authentication is successful,
    they'll be redirected back via Apros and the LMS to your mobile scheme URL, `scheme://sso/...`.
1.  The mobile app scheme will redirect the user back to your app, to be handled by the logic
    implemented in Step 2 above.
