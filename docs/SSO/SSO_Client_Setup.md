Single Sign-On: Requirements and Setup for McKinsey Academy Clients
===================================================================

McKinsey Academy supports single sign-on, which allows our clients’ employees to authenticate and login to McKinsey
Academy using their corporate Identity Provider (IdP), rather than a username and password.

Specifically, McKinsey Academy supports SAML 2.0 and is a SAML Service Provider (SP) that can be connected to corporate
IdPs (Identity Providers). McKinsey Academy uses OneLogin's SAML Python Toolkit to implement SAML, and supports most
SAML-compliant IdPs.

Identity Provider (IdP) Requirements
------------------------------------

To integrate with McKinsey Academy, your IdP *must*:

1. Support SAML 2.0
2. Support an *SP-initiated* SSO exchange, where the McKinsey Academy SP sends a SAML Request to the IdP using the
   HTTP-Redirect binding, and the IdP returns the SAML Response to the SP Assertion Consumer Service using the HTTP-POST
   binding. (**An IdP-initiated SSO exchange is not currently supported.**)
3. Provide at least the following attributes for each user in the assertion:
    ```
    Full name      cn            urn:oid:2.5.4.3
    Given name     givenName     urn:oid:2.5.4.42
    Surname        sn            urn:oid:2.5.4.4
    Email          mail          urn:oid:0.9.2342.19200300.100.1.3
    -- And, optionally (but recommended): --
    Username/ID    uid           urn:oid:0.9.2342.19200300.100.1.1
    City           city          (custom field ID, up to you)
    ```

Further, to make integration with McKinsey Academy easier and faster, your IdP *should*:

4. Have a publicly accessible IdP metadata XML URL that uses HTTPS.  E.g.,

        https://www.testshib.org/metadata/testshib-providers.xml

5. Have a separate staging IdP and production IdP, with test user accounts on the staging IdP that can be provided to
   McKinsey Academy staff for the purposes of debugging SAML integration issues.

   E.g., provide McKinsey Academy with several accounts like `testuser1@stage.idp.examplecorp.com`, including the
   passwords to those accounts. These test accounts should be on the stage IdP only and should not have any meaningful
   access to any systems other than the IdP itself.

McKinsey Academy Service Provider (SP) Details
----------------------------------------------

Please use the following information to configure an IdP to integrate with McKinsey Academy:

<table>
<tr>
<th>Stage SP metadata</th>
<td>https://stage.mckinsey.edx.org/auth/saml/metadata.xml</td>
</tr>
<tr>
<th>Stage SP Entity ID</th>
<td>https://stage.mckinsey.edx.org/ (also specified in the metadata)</td>
</tr>
<tr>
<th>Prod SP metadata</th>
<td>https://www.mckinseyacademy.com/auth/saml/metadata.xml</td>
</tr>
<tr>
<th>Prod SP Entity ID</th>
<td>http://www.mckinseyacademy.com/ (also specified in the metadata)</td>
</tr>
<tr>
<th>ACS URLs</th>
<td>(specified in the metadata)</td>
</tr>
<tr>
<th>Assertion attributes</th>
<td>See <a href="#identity-provider-idp-requirements">IdP requirement 3</a>, above.</td>
</tr>
<tr>
<th>Encrypt assertions</th>
<td>Not required.</td>
</tr>
<tr>
<th>Software used</th>
<td>SAML Python Toolkit by OneLogin</td>
</tr>
</table>

Integration Procedure
---------------------

1. Provide McKinsey Academy with the following information:
    * Name and version of the software you are using as the SAML IdP.
    * URL to the IdP’s metadata XML for both the staging and production IdP, or a file(s) containing the XML (see
      [requirement 4](#identity-provider-idp-requirements)). A URL is preferred.
    * List of SAML attributes that will be included in the assertion
      (see [requirement 3](#identity-provider-idp-requirements)).
    * Provide an example value for the UID attribute (if it’s a human-readable username like `jsmith`, we will use it as
      the user’s McKinsey Academy username if possible; if it’s an email address or a numeric ID, then the SP will
      automatically derive a username to be used within McKinsey Academy from the `First Name` attribute
    * Username(s) and password(s) of the restricted test accounts on the staging IdP, so McKinsey Academy staff can test
      the integration and debug issues.
      We recommend that you send the usernames via email and the passwords via https://onetimesecret.com/.
      If you are unable to provide restricted test accounts, please identify one or more people who will be available to
      test the integration, while sharing their screen if necessary.
1. Configure your stage IdP to support McKinsey Academy’s stage SP, using the details provided above.
1. McKinsey Academy will configure and test the integration with the stage SP.
1. Work together with McKinsey Academy to adjust IdP and/or SP configuration as required until the integration is working.
1. Configure your production IdP to support McKinsey Academy’s production SP, using the details provided above.

User Access via SSO
-------------------

Once SSO is configured, McKinsey Academy staff will provide your corporate learning team with one or more
**auto-enrollment links**. These links are unique to both your company and the specific program(s) or cours(es) that
your users may be taking. The links will look something like:

    https://www.mckinseyacademy.com/access/aa11bb22-cc33-4455-89fc-7202e4c931c6

Any user who clicks on one of these auto-enrollment links will be redirected to your company’s IdP. The IdP may then ask
them to authenticate and/or authorize McKinsey Academy to receive their user information. Next, they will be redirected
to McKinsey Academy, where a new user account will be automatically created. They will then be automatically enrolled
into the course(s) in their program.

Using an auto-enrollment link is the only supported way for new users to login to McKinsey Academy via SSO. It is
currently not possible to create a new account for an SSO user via any other means.

Once the user’s account has been created using an auto-enrollment link, the user may login to McKinsey Academy by
starting at https://www.mckinseyacademy.com/, clicking `Login`, clicking `SSO users click here`, and entering their
email address; they will then be authenticated via their IdP and able to access their McKinsey Academy account.

Alternatively, they can click on the auto-enrollment link again, which will then seamlessly log them in to McKinsey
Academy.

Single Logout (SLO)
-------------------

McKinsey Academy does not currently support single logout (SLO).
