

(function(globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    var v=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  var newcatalog = {
    " day": " dag", 
    " week": " week", 
    "# of people": "aantal personen", 
    "% total cohort": "% totale groep", 
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s Cursus gelabeld met %(tagDetails)s", 
      "%(count)s Cursussen gelabeld met %(tagDetails)s"
    ], 
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s Voordat de cursus begint, kunt u deze site verkennen voor meer informatie over wat u kunt verwachten.", 
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s van de %(cnt)s geselecteerd", 
      "%(sel)s van de %(cnt)s geselecteerd"
    ], 
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "%(selectedRows)s De deelnemers worden ingeschreven voor de cursus die hieronder is geselecteerd.", 
      "%(selectedRows)s De deelnemer wordt ingeschreven voor de cursus die hieronder is geselecteerd."
    ], 
    "%(value)s%": "%(value)s%", 
    "%s invalid email was ignored.": [
      "%s ongeldig e-mailadres is genegeerd.", 
      "%s ongeldige e-mailadressen zijn genegeerd.", 
      "%s ongeldige e-mailadressen zijn genegeerd.", 
      "%s ongeldige e-mailadressen zijn genegeerd.", 
      "%s ongeldige e-mailadressen zijn genegeerd.", 
      "%s ongeldige e-mailadressen zijn genegeerd."
    ], 
    "%s learner has been added to this cohort.": [
      "%s leerling is toegevoegd aan deze groep.", 
      "%s leerlingen zijn toegevoegd aan deze groep.", 
      "%s leerlingen zijn toegevoegd aan deze groep.", 
      "%s leerlingen zijn toegevoegd aan deze groep.", 
      "%s leerlingen zijn toegevoegd aan deze groep.", 
      "%s leerlingen zijn toegevoegd aan deze groep."
    ], 
    "%s learner has been moved to this cohort.": [
      "%s leerling is verplaatst naar deze groep.", 
      "%s leerlingen zijn verplaatst naar deze groep.", 
      "%s leerlingen zijn verplaatst naar deze groep.", 
      "%s leerlingen zijn verplaatst naar deze groep.", 
      "%s leerlingen zijn verplaatst naar deze groep.", 
      "%s leerlingen zijn verplaatst naar deze groep."
    ], 
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "%s leerling is vooraf aan deze groep toegevoegd. Deze leerling wordt automatisch toegevoegd aan de groep zodra hij/zij zich voor de cursus inschrijft.", 
      "%s leerlingen zijn vooraf aan deze groep toegevoegd. Deze leerlingen worden automatisch toegevoegd aan de groep zodra ze zich voor de cursus inschrijven.", 
      "%s leerlingen zijn vooraf aan deze groep toegevoegd. Deze leerlingen worden automatisch toegevoegd aan de groep zodra ze zich voor de cursus inschrijven.", 
      "%s leerlingen zijn vooraf aan deze groep toegevoegd. Deze leerlingen worden automatisch toegevoegd aan de groep zodra ze zich voor de cursus inschrijven.", 
      "%s leerlingen zijn vooraf aan deze groep toegevoegd. Deze leerlingen worden automatisch toegevoegd aan de groep zodra ze zich voor de cursus inschrijven.", 
      "%s leerlingen zijn vooraf aan deze groep toegevoegd. Deze leerlingen worden automatisch toegevoegd aan de groep zodra ze zich voor de cursus inschrijven."
    ], 
    "%s user was already in this cohort.": [
      "%s gebruiker zat al in deze groep.", 
      "%s gebruikers zaten al in deze groep.", 
      "%s gebruikers zaten al in deze groep.", 
      "%s gebruikers zaten al in deze groep.", 
      "%s gebruikers zaten al in deze groep.", 
      "%s gebruikers zaten al in deze groep."
    ], 
    "%s user/email was not found.": [
      "%s gebruiker/e-mailadres is niet gevonden.", 
      "%s gebruikers/e-mailadressen zijn niet gevonden.", 
      "%s gebruikers/e-mailadressen zijn niet gevonden.", 
      "%s gebruikers/e-mailadressen zijn niet gevonden.", 
      "%s gebruikers/e-mailadressen zijn niet gevonden.", 
      "%s gebruikers/e-mailadressen zijn niet gevonden."
    ], 
    ".0%": ",0%", 
    "2 or more fields can not have the same name": "2 of meer velden kunnen niet dezelfde naam hebben", 
    "6 a.m.": "6 uur 's ochtends", 
    "6 p.m.": "6 uur 's avonds", 
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "<span class=\"green\"> %(diff)s punt</span> boven het gemiddelde van uw organisatie", 
      "<span class=\"green\"> %(diff)s punten</span> boven het gemiddelde van uw organisatie", 
      "<span class=\"green\"> %(diff)s punten</span> boven het gemiddelde van uw organisatie", 
      "<span class=\"green\"> %(diff)s punten</span> boven het gemiddelde van uw organisatie", 
      "<span class=\"green\"> %(diff)s punten</span> boven het gemiddelde van uw organisatie", 
      "<span class=\"green\"> %(diff)s punten</span> boven het gemiddelde van uw organisatie"
    ], 
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "<span class=\"green\">%(diff)s% </span> boven het gemiddelde van uw organisatie", 
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "<span class=\"red\"> %(diff)s punt</span> onder het gemiddelde van uw organisatie", 
      "<span class=\"red\"> %(diff)s punten</span> onder het gemiddelde van uw organisatie", 
      "<span class=\"red\"> %(diff)s punten</span> onder het gemiddelde van uw organisatie", 
      "<span class=\"red\"> %(diff)s punten</span> onder het gemiddelde van uw organisatie", 
      "<span class=\"red\"> %(diff)s punten</span> onder het gemiddelde van uw organisatie", 
      "<span class=\"red\"> %(diff)s punten</span> onder het gemiddelde van uw organisatie"
    ], 
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "<span class=\"red\"> %(diff)s% </span> onder het gemiddelde van uw organisatie", 
    "Activated": "Geactiveerd", 
    "Activation File": "Activeringsbestand", 
    "Activation Link": "Activeringslink", 
    "Active": "Actief", 
    "Add new role e.g CEO,CTO": "Nieuwe functie toevoegen, zoals CEO,CTO", 
    "Admin Company": "Beheerder van bedrijf", 
    "Admin Permissions": "Beheerrechten", 
    "All students added to private group have to be members of same company.": "Alle studenten die aan een priv\u00e9groep worden toegevoegd, moeten leden zijn van hetzelfde bedrijf.", 
    "An error occurred submitting the request.": "Er trad een fout op tijdens het indienen van het verzoek.", 
    "Analytics URL": "URL Analyses", 
    "Android DL URL": "DL-URL Android", 
    "App Name": "App-naam", 
    "April": "april", 
    "Are you sure you want to remove this ?": "Weet u zeker dat u deze verwijdering wilt uitvoeren?", 
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "Weet u zeker dat u deze groep wilt verwijderen? Als u dat doet, worden de indieningen en feedback die aan de groep zijn gekoppeld, verwijderd.", 
    "Are you sure?": "Weet u het zeker?", 
    "Assessment: %(label)s": "Beoordeling: %(label)s", 
    "August": "augustus", 
    "Available %s": "Beschikbare %s", 
    "Avg Progress": "Gem. voortgang", 
    "Business Function": "Bedrijfsfunctie", 
    "Business Unit": "Bedrijfseenheid", 
    "Cancel": "Annuleren", 
    "Change Status": "Status wijzigen", 
    "Change status of all selected participants to:": "De status van alle geselecteerde deelnemers wijzigen in:", 
    "Check for Completion": "Voltooiing controleren", 
    "Choose": "Kiezen", 
    "Choose a Date": "Kies een datum", 
    "Choose a Time": "Kies een tijdstip", 
    "Choose a time": "Kies een tijd", 
    "Choose all": "Kies alle", 
    "Chosen %s": "Gekozen %s", 
    "Click Add to specify Lesson Label": "Klik op Toevoegen om Leslabel op te geven", 
    "Click Add to specify Lessons Label": "Klik op Toevoegen om Lessenlabel op te geven", 
    "Click Add to specify Module Label": "Klik op Toevoegen om Modulelabel op te geven", 
    "Click Add to specify Modules Label": "Klik op Toevoegen om Modulenlabel op te geven", 
    "Click to choose all %s at once.": "Klik om alle %s te kiezen.", 
    "Click to remove all chosen %s at once.": "Klik om alle gekozen %s tegelijk te verwijderen.", 
    "Cohort": "Cohort", 
    "Cohort Comp.": "Bedrijfscohort", 
    "Company": "Bedrijf", 
    "Company Admin": "Bedrijfsbeheer", 
    "Company ID": "Bedrijfs-id", 
    "Company doesn't exist! ": "Bedrijf bestaat niet!", 
    "Complete": "Voltooid", 
    "Complete all content to continue": "Voltooi alle inhoud om verder te gaan", 
    "Complete all content to continue.": "Voltooi alle inhoud om verder te gaan", 
    "Completed": "Voltooid", 
    "Contains Errors": "Bevat fouten", 
    "Content is complete, please continue.": "Inhoud voltooid, ga verder", 
    "Couldn't add tag to course!": "Kan geen tag aan de cursus toevoegen!", 
    "Couldn't create new company!": "Kan geen nieuw bedrijf maken!", 
    "Couldn't create new tag!": "Kan geen nieuwe tag maken!", 
    "Couldn't delete tag!": "Kan tag niet verwijderen!", 
    "Couldn't delink App!": "Kan deze app niet ontkoppelen!", 
    "Couldn't link this App!": "Kan deze app niet koppelen!", 
    "Country": "Land", 
    "Course": "Cursus", 
    "Course ID": "Cursus-id", 
    "Course Name": "Cursusnaam", 
    "Dashboard Name": "Dashboardnaam", 
    "Date Added": "Toevoegingsdatum", 
    "December": "december", 
    "Delete Role": "Functie wissen", 
    "Deployment Mech": "Implementatiemechanisme", 
    "Digital Content": "Digitale inhoud", 
    "Digital Course": "Digitale cursus", 
    "Do you really want to delete: \n": "Weet u zeker dat u de volgende verwijdering wilt uitvoeren: \n", 
    "Download": "Downloaden", 
    "Download CSV File": "CSV-bestand downloaden", 
    "Download Notifications CSV": "CSV-meldingen downloaden", 
    "Email": "E-mail", 
    "Email Preview Success!": "Het e-mailvoorbeeld is gelukt!", 
    "Email Success!": "E-mail is gelukt!", 
    "Email can't be empty! ": "E-mailadres mag niet leeg zijn!", 
    "End": "Einde", 
    "End Date": "Einddatum", 
    "End time": "Einddatum", 
    "Engagement": "Inzet", 
    "Enroll Participant": "Deelnemer inschrijven", 
    "Enroll Participants": "Deelnemers inschrijven", 
    "Enroll this list in another course": "Deze lijst inschrijven voor een andere cursus", 
    "Enrolled In": "Ingeschreven voor", 
    "Error File": "Foutmeldingsbestand", 
    "Error Occured!": "Fout opgetreden!", 
    "Error initiating the report generation. Please retry later.": "Taakuitvoering is mislukt. Probeer het later opnieuw.", 
    "Error processing CSV file.": "Fout bij verwerken CSV-bestand.", 
    "Error uploading file. Please try again and be sure to use an accepted file format.": "Fout bij uploaden van bestand. Probeer het opnieuw en zorg ervoor dat u een geaccepteerd bestandsformaat gebruikt.", 
    "Export Report": "Rapport exporteren", 
    "Exporting Stats for All Users": "Statistieken voor alle gebruikers exporteren", 
    "February": "februari", 
    "Female": "Vrouw", 
    "Fetching data for file: %(filename)s": "Gegevens ophalen voor bestand: %(filename)s", 
    "File name": "Bestandsnaam", 
    "File successfully uploaded!": "Het bestand is ge\u00fcpload!", 
    "Filename": "Bestandsnaam", 
    "Filter": "Filter", 
    "First name can't be empty! ": "Voornaam mag niet leeg zijn!", 
    "Go to %(course_id)s Course": "Ga naar %(course_id)s cursus", 
    "Grade": "Cijfer", 
    "Group Work: %(label)s": "Groepswerk: %(label)s", 
    "Group successfully updated": "Groep is bijgewerkt", 
    "Group was not created": "Groep is niet aangemaakt", 
    "Group work": "Groepswerk", 
    "Hide": "Verbergen", 
    "Hide Details": "Gegevens verbergen", 
    "Hide password": "Wachtwoord verbergen", 
    "I'm Done": "Ik ben klaar", 
    "Importing %(processed)s of %(total)s rows": "%(processed)s van %(total)s rijen importeren", 
    "Importing..": "Importeren...", 
    "In Person Session": "Klassikale sessie", 
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "Vooruitgangsanalyse toevoegen voor elke les (let op: het exporteren kost meer tijd)", 
    "Incomplete": "Onvolledig", 
    "Initiated by": "Ge\u00efnitieerd door", 
    "Invalid format for CSV file.": "Ongeldig formaat voor CSV-bestand.", 
    "It looks like you're not active. Click OK to keep working.": "Het lijkt erop dat u niet actief bent. Klik op OK om te blijven werken.", 
    "It looks like your browser settings has pop-ups disabled.": "Blijkbaar heb je in je browserinstellingen pop-ups geblokkeerd.", 
    "January": "januari", 
    "July": "juli", 
    "June": "juni", 
    "Last Log In": "Laatste aanmelding", 
    "Last name can't be empty! ": "Achternaam mag niet leeg zijn!", 
    "Launch pop-up to continue": "Pop-up toestaan om verder te gaan", 
    "Learner email": "E-mail leerling", 
    "Lesson": "Les", 
    "Male": "Man", 
    "Manager email": "E-mail manager", 
    "March": "maart", 
    "May": "mei", 
    "Midnight": "Middernacht", 
    "Moderator": "Moderator", 
    "Module": "Module", 
    "Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.": "Moet ten minste 8 tekens lang zijn en hoofdletters en kleine letters bevatten, plus cijfers OF speciale tekens.", 
    "Name": "Naam", 
    "No App Display Name!": "Geen app-weergavenaam!", 
    "No Company Display Name!": "Geen bedrijfsweergavenaam!", 
    "No file Selected": "Geen bestand geselecteerd", 
    "No. of Courses": "Aantal cursussen", 
    "No. of Participants": "Aantal deelnemers", 
    "NoName": "Naamloos", 
    "None": "Geen", 
    "Noon": "12 uur 's middags", 
    "Note: You are %s hour ahead of server time.": [
      "Let op: U ligt %s uur voor ten opzichte van de server-tijd.", 
      "Let op: U ligt %s uren voor ten opzichte van de server-tijd."
    ], 
    "Note: You are %s hour behind server time.": [
      "Let op: U ligt %s uur achter ten opzichte van de server-tijd.", 
      "Let op: U ligt %s uren achter ten opzichte van de server-tijd."
    ], 
    "Notification": "Melding", 
    "November": "november", 
    "Now": "Nu", 
    "Observer": "Waarnemer", 
    "October": "oktober", 
    "Only alphanumeric characters and spaces allowed": "Alleen alfanumerieke tekens en spaties toegestaan", 
    "Participant": "Deelnemer", 
    "Participants": "Deelnemers", 
    "Please enter new template name!": "Voer een nieuwe sjabloonnaam in!", 
    "Please enter preview email!": "Voer een nieuwe voorbeeldmail in!", 
    "Please enter updated template name or leave the old one!": "Voer een bijgewerkte sjabloonnaam in of laat de oude naam staan!", 
    "Please select at least one course": "Selecteer ten minste \u00e9\u00e9n cursus", 
    "Please select at least one student": "Selecteer ten minste \u00e9\u00e9n student", 
    "Please select file first.": "Selecteer eerst een bestand.", 
    "Please select file for upload.": "Selecteer een te uploaden bestand.", 
    "Please select project": "Selecteer een project", 
    "Poll/Survey Question": "Peiling/onderzoeksvraag", 
    "Preview Email!": "Voorbeeldmail!", 
    "Proficiency": "Vaardigheid", 
    "Program": "Programma", 
    "Progress": "Vooruitgang", 
    "Progress : 0%": "Vooruitgang: 0%", 
    "Progress: %(progress)s %": "Vooruitgang: %(progress)s %", 
    "Progress: %(value)s%": "Vooruitgang: %(value)s%", 
    "Remove": "Verwijderen", 
    "Remove all": "Verwijder alles", 
    "Report of bulk update will be sent to your email.": "Rapport voor bulk-update wordt naar uw e-mailadres verzonden.", 
    "Request Time": "Verzoektijd", 
    "Save Changes": "Wijzigingen opslaan", 
    "Search by Keyword": "Zoeken op Trefwoord", 
    "Select Course": "Cursus selecteren", 
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "Geselecteerd: %(selected)s, geslaagd: %(successful)s, niet geslaagd: %(failed)s", 
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "Geselecteerd: %(selectedRows)s, geslaagd: 0, niet geslaagd: 0", 
    "Send": "Verzenden", 
    "Send Course Intro Email": "Introductie-email voor cursus verzenden", 
    "September": "september", 
    "Show": "Tonen", 
    "Show Errors": "Fouten weergeven", 
    "Show password": "Wachtwoord weergeven", 
    "Start": "Begin", 
    "Start time": "Begindatum", 
    "Status": "Status", 
    "Successful": "Gelukt", 
    "Successfully Enrolled in 1 Course": "Ingeschreven voor 1 cursus", 
    "Successfully added new template!": "De sjabloon is toegevoegd!", 
    "Successfully deleted template!": "De sjabloon is verwijderd!", 
    "Successfully sent email!": "E-mail is verzonden!", 
    "Successfully sent preview email!": "De voorbeeldmail is verzonden!", 
    "Successfully updated template!": "De sjabloon is bijgewerkt!", 
    "TA": "OA", 
    "Task failed to execute. Please retry later.": "Taakuitvoering is mislukt. Probeer het later opnieuw.", 
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "Het .csv-bestand heeft meer dan %(limit)s rijen: %(lines)s , splits het bestand op in meerdere bestanden!", 
    "The content takes place in a new window.": "De inhoud wordt weergegeven in een nieuw venster.", 
    "There was an error submitting your file.": "Er trad een fout op tijdens het indienen van uw bestand.", 
    "This app name cannot contain non-alphanumeric characters!": "De app-naam mag enkel alfanumerieke tekens bevatten!", 
    "This app name cannot have more than 30 characters!": "De app-naam mag niet meer dan 30 tekens bevatten!", 
    "This company name cannot contain non-alphanumeric characters!": "De bedrijfsnaam mag geen alfanumerieke tekens bevatten!", 
    "This company name cannot have more than 30 characters!": "De bedrijfsnaam mag niet meer dan 30 tekens bevatten!", 
    "This field is required.": "This field is required.", 
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Dit is de lijst met beschikbare %s. U kunt kiezen uit een aantal door ze te selecteren in het vak hieronder en vervolgens op de \"Kiezen\" pijl tussen de twee lijsten te klikken.", 
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Dit is de lijst van de gekozen %s. Je kunt ze verwijderen door ze te selecteren in het vak hieronder en vervolgens op de \"Verwijderen\" pijl tussen de twee lijsten te klikken.", 
    "This tag name cannot contain non-alphanumeric characters!": "De tagnaam mag enkel alfanumerieke tekens bevatten!", 
    "This tag name cannot have more than 30 characters!": "De tagnaam mag niet meer dan 30 tekens bevatten!", 
    "Today": "Vandaag", 
    "Tomorrow": "Morgen", 
    "Try selecting your company from the type-ahead results.": "Probeer uw bedrijf te selecteren via de auto-aanvulresultaten.", 
    "Type into this box to filter down the list of available %s.": "Type in dit vak om te filteren in de lijst met beschikbare %s.", 
    "Unenroll": "Inschrijving opheffen", 
    "Unenroll Participants": "Inschrijving deelnemers opheffen", 
    "Unenroll all selected participants from this course?": "Wilt u de inschrijving van alle geselecteerde deelnemers voor deze cursus opheffen?", 
    "Updated user data!": "Gebruikersgegevens bijgewerkt!", 
    "Urban Airship URL": "URL Urban Airship", 
    "User successfully enrolled in course": "De gebruiker is ingeschreven voor de cursus", 
    "User will be enrolled in course selected below.": "De gebruiker wordt ingeschreven voor de cursus die hieronder is geselecteerd.", 
    "Username": "Gebruikersnaam", 
    "Username can't be empty! ": "Gebruikersnaam mag niet leeg zijn!", 
    "View Details": "Gegevens weergeven", 
    "We'll e-mail you when your report is ready to download.": "We sturen u een e-mail wanneer uw rapport klaar is om te downloaden.", 
    "Webinar": "Webinar", 
    "Welcome to McKinsey Academy": "Welkom bij McKinsey Academy", 
    "What would you like to do now?": "Wat wilt u nu doen?", 
    "Yesterday": "Gisteren", 
    "You are about to delete email template. Are you sure?": "U staat op het punt om de e-mailsjabloon te verwijderen. Weet u het zeker?", 
    "You can only add up to 4 fields": "U kunt niet meer dan 4 velden toevoegen", 
    "You don't have permission to create a new tag, please select one from the list!": "U beschikt niet over de machtiging voor het maken van een nieuwe tag. Selecteer een tag in de lijst!", 
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "U heeft een actie geselecteerd en heeft geen wijzigingen gemaakt op de individuele velden. U zoekt waarschijnlijk naar de Gaan knop in plaats van de Opslaan knop.", 
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "U heeft een actie geselecteerd, maar heeft de wijzigingen op de individuele velden nog niet opgeslagen. Klik alstublieft op OK om op te slaan. U zult vervolgens de actie opnieuw moeten uitvoeren.", 
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "U heeft niet opgeslagen wijzigingen op enkele indviduele velden. Als u nu een actie uitvoert zullen uw wijzigingen verloren gaan.", 
    "You need to enter course ID!": "U moet een cursus-id invoeren!", 
    "You need to enter name!": "U moet een naam invoeren!", 
    "You need to select at least one participant to be able to apply bulk actions.": "U moet ten minste \u00e9\u00e9n deelnemer selecteren om dergelijke bulkacties te kunnen toepassen.", 
    "You need to select course!": "U moet een cursus selecteren!", 
    "You need to select status!": "U moet een status selecteren!", 
    "You were logged out due to inactivity. Please log back in to continue.": "U bent uitgelogd vanwege inactiviteit. Log opnieuw in om door te gaan.", 
    "Your Progress: %(value)s%": "Uw voortgang: %(value)s%", 
    "Your course begins in %(days)s day.": [
      "Uw cursus begint over %(days)s dag.", 
      "Uw cursus begint over %(days)s dagen.", 
      "Uw cursus begint over %(days)s dagen.", 
      "Uw cursus begint over %(days)s dagen.", 
      "Uw cursus begint over %(days)s dagen.", 
      "Uw cursus begint over %(days)s dagen."
    ], 
    "Your course hasn't begun yet. ": "Uw cursus is nog niet begonnen. ", 
    "complete": "voltooien", 
    "contains %s learner": [
      "bevat %s leerling", 
      "bevat %s leerlingen", 
      "bevat %s leerlingen", 
      "bevat %s leerlingen", 
      "bevat %s leerlingen", 
      "bevat %s leerlingen"
    ], 
    "course id": "cursus-id", 
    "email": "e-mail", 
    "iOS DL URL": "DL-URL iOS", 
    "location": "locatie", 
    "one letter Friday\u0004F": "F", 
    "one letter Monday\u0004M": "M", 
    "one letter Saturday\u0004S": "S", 
    "one letter Sunday\u0004S": "S", 
    "one letter Thursday\u0004T": "T", 
    "one letter Tuesday\u0004T": "T", 
    "one letter Wednesday\u0004W": "W", 
    "same as your organization's average": "zelfde als het gemiddelde van uw organisatie", 
    "status": "status"
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
        return value[django.pluralidx(count)];
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
    "DATETIME_FORMAT": "j F Y H:i", 
    "DATETIME_INPUT_FORMATS": [
      "%d-%m-%Y %H:%M:%S", 
      "%d-%m-%y %H:%M:%S", 
      "%Y-%m-%d %H:%M:%S", 
      "%d/%m/%Y %H:%M:%S", 
      "%d/%m/%y %H:%M:%S", 
      "%Y/%m/%d %H:%M:%S", 
      "%d-%m-%Y %H:%M:%S.%f", 
      "%d-%m-%y %H:%M:%S.%f", 
      "%Y-%m-%d %H:%M:%S.%f", 
      "%d/%m/%Y %H:%M:%S.%f", 
      "%d/%m/%y %H:%M:%S.%f", 
      "%Y/%m/%d %H:%M:%S.%f", 
      "%d-%m-%Y %H.%M:%S", 
      "%d-%m-%y %H.%M:%S", 
      "%d/%m/%Y %H.%M:%S", 
      "%d/%m/%y %H.%M:%S", 
      "%d-%m-%Y %H.%M:%S.%f", 
      "%d-%m-%y %H.%M:%S.%f", 
      "%d/%m/%Y %H.%M:%S.%f", 
      "%d/%m/%y %H.%M:%S.%f", 
      "%d-%m-%Y %H:%M", 
      "%d-%m-%y %H:%M", 
      "%Y-%m-%d %H:%M", 
      "%d/%m/%Y %H:%M", 
      "%d/%m/%y %H:%M", 
      "%Y/%m/%d %H:%M", 
      "%d-%m-%Y %H.%M", 
      "%d-%m-%y %H.%M", 
      "%d/%m/%Y %H.%M", 
      "%d/%m/%y %H.%M", 
      "%d-%m-%Y", 
      "%d-%m-%y", 
      "%Y-%m-%d", 
      "%d/%m/%Y", 
      "%d/%m/%y", 
      "%Y/%m/%d"
    ], 
    "DATE_FORMAT": "j F Y", 
    "DATE_INPUT_FORMATS": [
      "%d-%m-%Y", 
      "%d-%m-%y", 
      "%d/%m/%Y", 
      "%d/%m/%y", 
      "%Y-%m-%d"
    ], 
    "DECIMAL_SEPARATOR": ",", 
    "FIRST_DAY_OF_WEEK": "1", 
    "MONTH_DAY_FORMAT": "j F", 
    "NUMBER_GROUPING": "3", 
    "SHORT_DATETIME_FORMAT": "j-n-Y H:i", 
    "SHORT_DATE_FORMAT": "j-n-Y", 
    "THOUSAND_SEPARATOR": ".", 
    "TIME_FORMAT": "H:i", 
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S", 
      "%H:%M:%S.%f", 
      "%H.%M:%S", 
      "%H.%M:%S.%f", 
      "%H.%M", 
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

