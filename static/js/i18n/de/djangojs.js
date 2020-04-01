

(function(globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    var v=(n != 1);
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  var newcatalog = {
    " day": " Tag",
    " week": " Woche",
    "# of people": "Anzahl von Personen",
    "% total cohort": "% des Jahrgangs",
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s Der Kurs wurde mit %(tagDetails)s markiert",
      "%(Zahl)s Die Kurse wurden mit %(tagDetails)s markiert"
    ],
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s Bevor Ihr Kurs beginnt, k\u00f6nnen Sie die Seite erkunden, um mehr dar\u00fcber zu erfahren, was Sie erwartet.",
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s von %(cnt)s ausgew\u00e4hlt",
      "%(sel)s von %(cnt)s ausgew\u00e4hlt"
    ],
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "%(selectedRows)s Teilnehmer werden bei dem unten ausgew\u00e4hlten Kurs angemeldet.",
      "%(selectedRows)s Teilnehmer werden bei dem unten ausgew\u00e4hlten Kurs angemeldet."
    ],
    "%(value)s%": "%(value)s%",
    "%s invalid email was ignored.": [
      "%s ung\u00fcltige E-Mail-Adresse wurde \u00fcbergangen.",
      "%s ung\u00fcltige E-Mail-Adressen wurden \u00fcbergangen."
    ],
    "%s learner has been added to this cohort.": [
      "%s Lerner wurde diesem Jahrgang hinzugef\u00fcgt.",
      "%s Lerner wurden diesem Jahrgang hinzugef\u00fcgt."
    ],
    "%s learner has been moved to this cohort.": [
      "%s Lerner ist in diesen Jahrgang gewechselt.",
      "%s Lerner sind in diesen Jahrgang gewechselt."
    ],
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "%s Lerner wurde diesem Jahrgang im Vorhinein hinzugef\u00fcgt. Dieser Lerner wird dem Jahrgang automatisch zugeordnet, wenn er sich zum Kurs anmeldet.",
      "%s Lerner wurden diesem Jahrgang im Vorhinein hinzugef\u00fcgt. Diese Lerner werden dem Jahrgang automatisch zugeordnet, wenn sie sich zum Kurs anmelden."
    ],
    "%s user was already in this cohort.": [
      "%s Nutzer war bereits in diesem Jahrgang.",
      "%s Nutzer waren bereits in diesem Jahrgang."
    ],
    "%s user/email was not found.": [
      "%s Nutzer/E-Mail-Adresse wurde nicht gefunden.",
      "%s Nutzer/E-Mail-Adressen wurden nicht gefunden."
    ],
    ".0%": ".0%",
    "2 or more fields can not have the same name": "2 oder mehr Felder k\u00f6nnen nicht denselben Namen haben",
    "6 a.m.": "6 Uhr",
    "6 p.m.": "18 Uhr",
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "<span class=\"green\"> %(diff)s point</span> \u00fcber dem Durchschnitt Ihrer Organisation",
      "<span class=\"green\"> %(diff)s points</span> \u00fcber dem Durchschnitt Ihrer Organisation"
    ],
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "<span class=\"green\">%(diff)s% </span> \u00fcber dem Durchschnitt Ihrer Organisation",
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "<span class=\"red\"> %(diff)s point</span> unter dem Durchschnitt Ihrer Organisation",
      "<span class=\"red\"> %(diff)s points</span> unter dem Durchschnitt Ihrer Organisation"
    ],
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "<span class=\"red\"> %(diff)s% </span> unter dem Durchschnitt Ihrer Organisation",
    "Activated": "Aktiviert",
    "Activation File": "Aktivierungs-Link",
    "Activation Link": "Aktivierungs-Link",
    "Active": "Aktiv",
    "Add new role e.g CEO,CTO": "F\u00fcgen Sie eine neue Rolle, z. B. CEO, CTO hinzu",
    "Admin Company": "Admin Firma",
    "Admin Permissions": "Admin-Berechtigungen",
    "All students added to private group have to be members of same company.": "Alle Teilnehmer, die zu der privaten Gruppe hinzugef\u00fcgt werden, m\u00fcssen der gleichen Firma angeh\u00f6ren.",
    "An error occurred submitting the request.": "Beim Einreichen der Anfrage ist ein Fehler aufgetreten.",
    "Analytics URL": "Analytics URL",
    "Android DL URL": "Android DL URL",
    "Announcements": "Ank\u00fcndigungen",
    "App Name": "App-Name",
    "April": "April",
    "Are you sure you want to remove this ?": "Sind Sie sicher, dass Sie das l\u00f6schen m\u00f6chten?",
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "Sind Sie sicher, dass Sie diese Gruppe l\u00f6schen m\u00f6chten? Alle in Verbindung mit dieser Gruppe eingereichten Dokumente sowie das Feedback werden dann gel\u00f6scht.",
    "Are you sure?": "Sind Sie sicher?",
    "Assessment: %(label)s": "Bewertung: %(label)s",
    "August": "August",
    "Available %s": "Verf\u00fcgbare %s",
    "Avg Progress": "Durchschnittlicher Fortschritt",
    "Business Function": "Gesch\u00e4ftsfunktion",
    "Business Unit": "Gesch\u00e4ftseinheit",
    "Cancel": "Abbrechen",
    "Change Status": "Status \u00e4ndern",
    "Change status of all selected participants to:": "Den Status aller ausgew\u00e4hlten Teilnehmer \u00e4ndern zu:",
    "Check for Completion": "Auf Vollst\u00e4ndigkeit pr\u00fcfen",
    "Choose": "Ausw\u00e4hlen",
    "Choose a Date": "Datum w\u00e4hlen",
    "Choose a Time": "Uhrzeit w\u00e4hlen",
    "Choose a time": "Uhrzeit",
    "Choose all": "Alle ausw\u00e4hlen",
    "Chosen %s": "Ausgew\u00e4hlte %s",
    "Click Add to specify Lesson Label": "Auf \"Hinzuf\u00fcgen\" klicken, um die Lektionsbeschriftung anzugeben",
    "Click Add to specify Lessons Label": "Auf \"Hinzuf\u00fcgen\" klicken, um die Lektionsbeschriftung anzugeben",
    "Click Add to specify Module Label": "Auf \"Hinzuf\u00fcgen\" klicken, um die Modulbeschriftung anzugeben",
    "Click Add to specify Modules Label": "Auf \"Hinzuf\u00fcgen\" klicken, um die Modulbeschriftung anzugeben",
    "Click to choose all %s at once.": "Klicken, um alle %s auf einmal auszuw\u00e4hlen.",
    "Click to remove all chosen %s at once.": "Klicken, um alle ausgew\u00e4hlten %s auf einmal zu entfernen.",
    "Cohort": "Jahrgang Firma",
    "Cohort Comp.": "Jahrgang Firma",
    "Company": "Firma",
    "Company Admin": "Firmen-Admin",
    "Company ID": "Firmen-ID",
    "Company doesn't exist! ": "Diese Firma existiert nicht! ",
    "Complete": "Vollst\u00e4ndig",
    "Complete all content to continue": "Zum Fortfahren Inhalt vervollst\u00e4ndigen",
    "Complete all content to continue.": "Zum Fortfahren Inhalt vervollst\u00e4ndigen",
    "Completed": "Abgeschlossen",
    "Contains Errors": "Enth\u00e4lt Fehler ",
    "Content is complete, please continue.": "Inhalt ist vollst\u00e4ndig, bitte fahren Sie fort",
    "Couldn't add tag to course!": "Diesem Kurs konnte kein Tag hinzugef\u00fcgt werden!",
    "Couldn't create new company!": "Eine neue Firma konnte nicht angelegt werden!",
    "Couldn't create new tag!": "Eine neues Tag konnte nicht erstellt werden!",
    "Couldn't delete tag!": "Das Tag konnte nicht gel\u00f6scht werden!",
    "Couldn't delink App!": "Diese App konnte nicht entkoppelt werden!",
    "Couldn't link this App!": "Diese App konnte nicht verbunden werden!",
    "Country": "Land",
    "Course": "Kurs",
    "Course ID": "Kurs-ID",
    "Course Name": "Kursname",
    "Dashboard Name": "Dashboard-Name",
    "Date Added": "Datum hinzugef\u00fcgt",
    "December": "Dezember",
    "Delete Role": "Rolle l\u00f6schen",
    "Deployment Mech": "Entwicklung Mech",
    "Digital Content": "Digitaler Inhalt",
    "Digital Course": "Digitaler Kurs",
    "Discussion": "Diskussionen",
    "Do you really want to delete: \n": "M\u00f6chten Sie Folgendes wirklich l\u00f6schen: \n",
    "Download": "Herunterladen",
    "Download CSV File": "CSV-Datei herunterladen",
    "Download Notifications CSV": "CSV-Benachrichtigungen herunterladen",
    "Email": "E-Mail",
    "Email Preview Success!": "Erfolgreiche Vorschau der E-Mail!",
    "Email Success!": "Erfolgreiche E-Mail!",
    "Email can't be empty! ": "E-Mail darf nicht leer sein! ",
    "End": "Ende",
    "End Date": "Datum der Fertigstellung",
    "End time": "Ende",
    "Engagement": "Engagement",
    "Enroll Participant": "Teilnehmer anmelden",
    "Enroll Participants": "Teilnehmer anmelden",
    "Enroll this list in another course": "Melde diese Liste in einem anderen Kurs an",
    "Enrolled In": "Angemeldet bei",
    "Error File": "Fehler Datei",
    "Error Occured!": "Fehler aufgetreten!",
    "Error initiating the report generation. Please retry later.": "Bei dem Start der Berichtgenerierung ist ein Fehler aufgetreten. Bitte versuchen Sie es sp\u00e4ter noch einmal.",
    "Error processing CSV file.": "Fehler bei der Verarbeitung der CVS-Datei.",
    "Error uploading file. Please try again and be sure to use an accepted file format.": "Die Datei konnte nicht hochgeladen werden. Bitte versuchen Sie es erneut. Stellen Sie dabei sicher, dass es sich um ein unterst\u00fctztes Dateiformat handelt.",
    "Export Report": "Bericht exportieren",
    "Exporting Stats for All Users": "Statistiken f\u00fcr alle Nutzer exportieren",
    "February": "Februar",
    "Female": "Weiblich",
    "Fetching data for file: %(filename)s": "Daten f\u00fcr die Datei: %(filename)s werden abgerufen",
    "File name": "Dateiname",
    "File successfully uploaded!": "Datei wurde erfolgreich hochgeladen!",
    "Filename": "Nutzername",
    "Filter": "Filter",
    "First name can't be empty! ": "Der Vorname darf nicht leer sein! ",
    "Go to %(course_id)s Course": "Gehe zu Kurs %(course_id)s ",
    "Grade": "Note",
    "Group Work": "Gruppenarbeit",
    "Group Work: %(label)s": "Gruppenarbeit: %(label)s",
    "Group successfully updated": "Die Gruppe wurde erfolgreich aktualisiert",
    "Group was not created": "Die Gruppe wurde nicht erstellt",
    "Group work": "Gruppenarbeit",
    "Hide": "Ausblenden",
    "Hide Details": "Details verbergen",
    "Hide password": "Passwort ausblenden",
    "I'm Done": "Fertig",
    "Importing %(processed)s of %(total)s rows": "Wird importiert %(Fortschritt)e von %(Gesamt) Reihen",
    "Importing..": "Wird importiert...",
    "In Person Session": "Pers\u00f6nlicher Unterrichtsabschnitt",
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "Aufschl\u00fcsselung des Fortschritts f\u00fcr jede Lektion erfassen (Hinweis: der Export wird mehr Zeit in Anspruch nehmen)",
    "Incomplete": "Unvollst\u00e4ndig",
    "Initiated by": "Eingeleitet von",
    "Invalid format for CSV file.": "Ung\u00fcltiges Format f\u00fcr CSV-Datei.",
    "It looks like you're not active. Click OK to keep working.": "Es scheint, als seien Sie nicht aktiv. Klicken Sie auf OK um weiterzuarbeiten.",
    "It looks like your browser settings has pop-ups disabled.": "Anscheinend wurden Pop-ups in Ihren Browser-Einstellungen deaktiviert.",
    "January": "Januar",
    "July": "Juli",
    "June": "Juni",
    "Last Log In": "Letzte Anmeldung",
    "Last name can't be empty! ": "Der Nachname darf nicht leer sein! ",
    "Launch pop-up to continue": "Zum Fortfahren Pop-up-Fenster \u00f6ffnen",
    "Leaderboards": "Ranglisten",
    "Learner email": "E-Mail des Lernenden",
    "Lesson": "Lektion",
    "Male": "M\u00e4nnlich",
    "Manager email": "E-Mail des Managers",
    "March": "M\u00e4rz",
    "May": "Mai",
    "Midnight": "Mitternacht",
    "Moderator": "Moderator",
    "Module": "Modul",
    "Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.": "Passwort Muss mindestens 8 Zeichen, Gro\u00df- und Kleinbuchstaben und Zahlen ODER Sonderzeichen enthalten.",
    "Name": "Name",
    "No App Display Name!": "Kein App-Name wird angezeigt!",
    "No Company Display Name!": "Kein Firmenname wird angezeigt!",
    "No file Selected": "Keine Datei ausgew\u00e4hlt",
    "No. of Courses": "Anzahl der Kurse",
    "No. of Participants": "Anzahl der Teilnehmer",
    "NoName": "Kein Name",
    "None": "Keine",
    "Noon": "Mittag",
    "Note: You are %s hour ahead of server time.": [
      "Achtung: Sie sind %s Stunde der Serverzeit vorraus.",
      "Achtung: Sie sind %s Stunden der Serverzeit vorraus."
    ],
    "Note: You are %s hour behind server time.": [
      "Achtung: Sie sind %s Stunde hinter der Serverzeit.",
      "Achtung: Sie sind %s Stunden hinter der Serverzeit."
    ],
    "Notification": "Benachrichtigung",
    "November": "November",
    "Now": "Jetzt",
    "Observer": "Beobachter",
    "October": "Oktober",
    "Only alphanumeric characters and spaces allowed": "Nur alphanumerische Zeichen und Leerzeichen erlaubt",
    "Participant": "Teilnehmer",
    "Participants": "Teilnehmer",
    "Please enter new template name!": "Bitte geben Sie einen neuen Vorlagennamen ein!",
    "Please enter preview email!": "Bitte geben Sie die Vorschau-E-Mail ein!",
    "Please enter updated template name or leave the old one!": "Bitte geben Sie einen aktualisierten Vorlagennamen ein oder bleiben Sie bei dem vorherigen Namen!",
    "Please select at least one course": "W\u00e4hlen Sie mindestens einen Kurs aus",
    "Please select at least one student": "Bitte w\u00e4hlen Sie mind. einen Teilnehmer",
    "Please select file first.": "Bitte w\u00e4hlen Sie zuerst eine Datei aus.",
    "Please select file for upload.": "W\u00e4hlen Sie eine Datei zum Hochladen aus.",
    "Please select project": "Bitte w\u00e4hlen Sie ein Projekt",
    "Poll/Survey Question": "Umfrage/Frage",
    "Preview Email!": "Vorschau-E-Mail!",
    "Proficiency": "Kompetenzen",
    "Program": "Programm",
    "Progress": "Fortschritt",
    "Progress : 0%": "Fortschritt : 0%",
    "Progress: %(progress)s %": "Fortschritt: %(progress)s %",
    "Progress: %(value)s%": "Fortschritt: %(value)s%",
    "Remove": "Entfernen",
    "Remove all": "Alle entfernen",
    "Report of bulk update will be sent to your email.": "Bericht der Massenaktualisierung wird an Ihre E-Mail-Adresse gesendet.",
    "Request Time": "Zeit f\u00fcr die Anfrage",
    "Save Changes": "\u00c4nderungen speichern",
    "Search by Keyword": "Nach Keywords suchen",
    "Select Course": "Kurs ausw\u00e4hlen",
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "Ausgew\u00e4hlt: %(selected)s, Bestanden: %(successful)s, Nicht bestanden: %/(failed)s",
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "Ausgew\u00e4hlt: %(selectedRows)s, Bestanden: 0, Nicht bestanden: 0",
    "Send": "Senden",
    "Send Course Intro Email": "Kurs-Einf\u00fchrungs-E-Mail senden",
    "September": "September",
    "Show": "Einblenden",
    "Show Errors": "Fehler anzeigen",
    "Show password": "Passwort anzeigen",
    "Start": "Start",
    "Start time": "Start",
    "Status": "Status",
    "Successful": "Erfolgreich",
    "Successfully Enrolled in 1 Course": "Erfolgreich zu einem Kurs angemeldet",
    "Successfully added new template!": "Neue Vorlage wurde erfolgreich hinzugef\u00fcgt!",
    "Successfully deleted template!": "Die Vorlage wurde erfolgreich gel\u00f6scht!",
    "Successfully sent email!": "E-Mail erfolgreich versendet!",
    "Successfully sent preview email!": "Erfolgreich versendete Vorschau-E-Mail!",
    "Successfully updated template!": "Die Vorlage wurde erfolgreich aktualisiert!",
    "TA": "TA",
    "Task failed to execute. Please retry later.": "Die Aufgabe konnte nicht ausgef\u00fchrt werden. Bitte versuchen Sie es sp\u00e4ter noch einmal.",
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "Die .csv-Datei hat mehr als %(limit)s Zeilen: %(lines)s , bitte teilen Sie die Datei in mehrere auf.",
    "The content takes place in a new window.": "Die Inhalte werden in einem neuen Fenster angezeigt.",
    "There was an error submitting your file.": "Beim Einreichen Ihrer Datei ist ein Fehler aufgetreten.",
    "This app name cannot contain non-alphanumeric characters!": "Dieser App-Name darf nur alphanumerische Zeichen beinhalten!",
    "This app name cannot have more than 30 characters!": "Dieser App-Name darf nicht mehr als 30 Zeichen beinhalten!",
    "This company name cannot contain non-alphanumeric characters!": "Dieser Firmenname darf nur alphanumerische Zeichen beinhalten!",
    "This company name cannot have more than 30 characters!": "Dieser Firmenname darf nicht mehr als 30 Zeichen beinhalten!",
    "This field is required.": "Dieses Feld ist erforderlich.",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Dies ist die Liste der verf\u00fcgbaren %s. Einfach im unten stehenden Feld markieren und mithilfe des \"Ausw\u00e4hlen\"-Pfeils ausw\u00e4hlen.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Dies ist die Liste der ausgew\u00e4hlten %s. Einfach im unten stehenden Feld markieren und mithilfe des \"Entfernen\"-Pfeils wieder entfernen.",
    "This tag name cannot contain non-alphanumeric characters!": "Dieser Tagname darf nur alphanumerische Zeichen beinhalten!",
    "This tag name cannot have more than 30 characters!": "Dieser Tagname darf nicht mehr als 30 Zeichen beinhalten!",
    "Today": "Heute",
    "Today at ": "heute",
    "Tomorrow": "Morgen",
    "Try selecting your company from the type-ahead results.": "Bitte w\u00e4hlen Sie Ihre Firma anhand der vorgeschlagenen Ergebnisse aus.",
    "Type into this box to filter down the list of available %s.": "Durch Eingabe in diesem Feld l\u00e4sst sich die Liste der verf\u00fcgbaren %s eingrenzen.",
    "Unenroll": "Abmelden",
    "Unenroll Participants": "Teilnehmer abmelden",
    "Unenroll all selected participants from this course?": "Alle ausgew\u00e4hlten Teilnehmer von diesem Kurs abmelden?",
    "Updated user data!": "Aktualisierte Nutzerdaten!",
    "Urban Airship URL": "Urban Airship URL",
    "User successfully enrolled in course": "Nutzer wurde erfolgreich bei dem Kurs angemeldet",
    "User will be enrolled in course selected below.": "Nutzer wird bei dem unten ausgew\u00e4hlten Kurs angemeldet.",
    "Username": "Nutzername",
    "Username can't be empty! ": "Der Nutzername darf nicht leer sein! ",
    "View Details": "Details ansehen",
    "We'll e-mail you when your report is ready to download.": "Wir senden Ihnen eine E-Mail, sobald Ihr Bericht zum Herunterladen bereit steht.",
    "Webinar": "Webinar",
    "Welcome to McKinsey Academy": "Willkommen bei der McKinsey Academy",
    "What would you like to do now?": "Was w\u00fcrden Sie jetzt gerne tun?",
    "Yesterday": "Gestern",
    "You are about to delete email template. Are you sure?": "Dadurch wird die E-Mail-Vorlage gel\u00f6scht. Sind Sie sicher?",
    "You are now": "Sie sind jetzt",
    "You can only add up to 4 fields": "Sie k\u00f6nnen nur bis zu 4 Felder hinzuf\u00fcgen",
    "You don't have permission to create a new tag, please select one from the list!": "Sie verf\u00fcgen nicht \u00fcber die Berechtigungen, um ein neues Tag zu erstellen. Bitte w\u00e4hlen Sie daher eines von der Liste!",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Sie haben eine Aktion ausgew\u00e4hlt, aber keine \u00c4nderungen an bearbeitbaren Feldern vorgenommen. Sie wollten wahrscheinlich auf \"Ausf\u00fchren\" und nicht auf \"Speichern\" klicken.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Sie haben eine Aktion ausgew\u00e4hlt, aber ihre vorgenommenen \u00c4nderungen nicht gespeichert. Klicken Sie OK, um dennoch zu speichern. Danach m\u00fcssen Sie die Aktion erneut ausf\u00fchren.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Sie haben \u00c4nderungen an bearbeitbaren Feldern vorgenommen und nicht gespeichert. Wollen Sie die Aktion trotzdem ausf\u00fchren und Ihre \u00c4nderungen verwerfen?",
    "You need to enter course ID!": "Bitte geben Sie die Kurs-ID ein!",
    "You need to enter name!": "Bitte geben Sie den Namen ein!",
    "You need to select at least one participant to be able to apply bulk actions.": "Mindestens ein Teilnehmer muss ausgew\u00e4hlt werden, um Massenoperationen anzuwenden.",
    "You need to select course!": "Sie m\u00fcssen einen Kurs ausw\u00e4hlen!",
    "You need to select status!": "Sie m\u00fcssen einen Status ausw\u00e4hlen!",
    "You were logged out due to inactivity. Please log back in to continue.": "Sie wurden aufgrund von Inaktivit\u00e4t ausgeloggt. Bitte loggen Sie sich wieder ein, um fortzufahren.",
    "Your Progress: %(value)s%": "Ihr Fortschritt: %(value)s%",
    "Your course begins in %(days)s day.": [
      "Ihr Kurs f\u00e4ngt in %(days)s Tag an.",
      "Ihr Kurs f\u00e4ngt in %(days)s Tagen an."
    ],
    "Your course hasn't begun yet. ": "Ihr Kurs hat noch nicht begonnen. ",
    "complete": "vollst\u00e4ndig",
    "contains %s learner": [
      "enth\u00e4lt %s Lerner",
      "enth\u00e4lt %s Lerner"
    ],
    "course id": "Kurs-ID",
    "email": "E-Mail",
    "for": "f\u00fcr",
    "iOS DL URL": "iOS DL URL",
    "in the cohort!": "in der Gruppe",
    "location": "Ort",
    "one letter Friday\u0004F": "Fr",
    "one letter Monday\u0004M": "Mo",
    "one letter Saturday\u0004S": "Sa",
    "one letter Sunday\u0004S": "So",
    "one letter Thursday\u0004T": "Do",
    "one letter Tuesday\u0004T": "Di",
    "one letter Wednesday\u0004W": "Mi",
    "same as your organization's average": "wie der Durchschnitt Ihrer Organisation",
    "status": "Status"
  };
  for (var key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }
  

  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      var value = django.catalog[msgid];
      if (typeof(value) == 'undefined') {
        return msgid;
      } else {
        return (typeof(value) == 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      var value = django.catalog[singular];
      if (typeof(value) == 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      var value = django.gettext(context + '\x04' + msgid);
      if (value.indexOf('\x04') != -1) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      var value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.indexOf('\x04') != -1) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "j. F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%d.%m.%Y",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. F Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d.m.Y H:i",
    "SHORT_DATE_FORMAT": "d.m.Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      var value = django.formats[format_type];
      if (typeof(value) == 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }

}(this));

