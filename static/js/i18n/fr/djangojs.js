

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
    " day": " jour",
    " week": " semaine",
    "# of people": "# de personnes",
    "% total cohort": "% total de la division",
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s Cours \u00e9tiquet\u00e9 avec %(tagDetails)s",
      "%(count)s Cours \u00e9tiquet\u00e9s avec %(tagDetails)s"
    ],
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s D\u2019ici l\u00e0, vous pouvez explorer ce site pour en savoir plus sur ce qui vous attend.",
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s sur %(cnt)s s\u00e9lectionn\u00e9",
      "%(sel)s sur %(cnt)s s\u00e9lectionn\u00e9s"
    ],
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "%(selectedRows)s Les participants seront inscrits au cours s\u00e9lectionn\u00e9 ci-dessous.",
      "%(selectedRows)s Le participant sera inscrit au cours s\u00e9lectionn\u00e9 ci-dessous."
    ],
    "%(value)s%": "%(value)s%",
    "%s invalid email was ignored.": [
      "%s e-mail invalide a \u00e9t\u00e9 ignor\u00e9.",
      "%s e-mail invalides ont \u00e9t\u00e9 ignor\u00e9s."
    ],
    "%s learner has been added to this cohort.": [
      "%s apprenant a \u00e9t\u00e9 ajout\u00e9 \u00e0 cette division.",
      "%s apprenants ont \u00e9t\u00e9 ajout\u00e9s \u00e0 cette division."
    ],
    "%s learner has been moved to this cohort.": [
      "%s apprenant a \u00e9t\u00e9 d\u00e9plac\u00e9 vers cette division.",
      "%s apprenants ont \u00e9t\u00e9 d\u00e9plac\u00e9s vers cette division."
    ],
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "%s apprenant a \u00e9t\u00e9 pr\u00e9-affect\u00e9 \u00e0 cette division. Cet apprenant sera automatiquement ajout\u00e9 \u00e0 la division lors de son inscription au cours.",
      "%s apprenants ont \u00e9t\u00e9 pr\u00e9-affect\u00e9s \u00e0 cette division. Ces apprenants seront automatiquement ajout\u00e9s \u00e0 la division lors de leur inscription au cours."
    ],
    "%s user was already in this cohort.": [
      "%s utilisateur \u00e9tait d\u00e9j\u00e0 dans cette division.",
      "%s utilisateurs \u00e9taient d\u00e9j\u00e0 dans cette division."
    ],
    "%s user/email was not found.": [
      "%s utilisateur/e-mail n\u2019a pas \u00e9t\u00e9 trouv\u00e9.",
      "%s utilisateurs/e-mail n\u2019ont pas \u00e9t\u00e9 trouv\u00e9s."
    ],
    ".0%": ",0\u00a0%",
    "2 or more fields can not have the same name": "Il est impossible de donner le m\u00eame nom \u00e0 deux champs ou plus",
    "6 a.m.": "6:00",
    "6 p.m.": "18:00",
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "<span class=\"green\"> %(diff)s point</span> au-dessus de la moyenne de votre organisation",
      "<span class=\"green\"> %(diff)s points</span> au-dessus de la moyenne de votre organisation"
    ],
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "<span class=\"green\">%(diff)s% </span> au-dessus de la moyenne de votre organisation",
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "<span class=\"red\"> %(diff)s point</span> en dessous de la moyenne de votre organisation",
      "<span class=\"red\"> %(diff)s points</span> en dessous de la moyenne de votre organisation"
    ],
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "<span class=\"red\"> %(diff)s% </span> en dessous de la moyenne de votre organisation",
    "Activated": "Activ\u00e9",
    "Activation File": "Fichier d\u2019activation",
    "Activation Link": "Lien d\u2019activation",
    "Active": "Active",
    "Add new role e.g CEO,CTO": "Ajouter un nouveau r\u00f4le, par exemple PDG, DT",
    "Admin Company": "Soci\u00e9t\u00e9 admin",
    "Admin Permissions": "Autorisations admin",
    "All students added to private group have to be members of same company.": "Tous les \u00e9tudiants ajout\u00e9s au groupe priv\u00e9 doivent \u00eatre des membres de la m\u00eame entreprise.",
    "An error occurred submitting the request.": "Une erreur s\u2019est produite lors de l\u2019envoi de la requ\u00eate.",
    "Analytics URL": "Analytics URL",
    "Android DL URL": "Android DL URL",
    "Announcements": "Annonces",
    "App Name": "Nom de l\u2019application",
    "April": "Avril",
    "Are you sure you want to remove this ?": "\u00cates-vous s\u00fbr de vouloir supprimer ceci\u00a0?",
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "\u00cates-vous s\u00fbr de vouloir supprimer ce groupe\u00a0? Ce faisant, vous supprimerez les envois et les commentaires associ\u00e9s au groupe.",
    "Are you sure?": "\u00cates-vous s\u00fbr\u00a0?",
    "Assessment: %(label)s": "\u00c9valuation\u00a0: %(label)s",
    "August": "Ao\u00fbt",
    "Available %s": "%s disponible(s)",
    "Avg Progress": "Progression moyenne",
    "Business Function": "Fonction commerciale",
    "Business Unit": "Unit\u00e9 commerciale",
    "Cancel": "Annuler",
    "Change Status": "Modifier le statut",
    "Change status of all selected participants to:": "Modifier le statut de tous les participants s\u00e9lectionn\u00e9s en\u00a0:",
    "Check for Completion": "V\u00e9rifier que la t\u00e2che est termin\u00e9e",
    "Choose": "Choisir",
    "Choose a Date": "Choisir une date",
    "Choose a Time": "Choisir une heure",
    "Choose a time": "Choisir une heure",
    "Choose all": "Tout choisir",
    "Chosen %s": "Choix des \u00ab\u00a0%s \u00bb",
    "Click Add to specify Lesson Label": "Cliquez sur \u00ab\u00a0Ajouter\u00a0\u00bb pour sp\u00e9cifier l\u2019\u00e9tiquette de la le\u00e7on",
    "Click Add to specify Lessons Label": "Cliquez sur \u00ab\u00a0Ajouter\u00a0\u00bb pour sp\u00e9cifier l\u2019\u00e9tiquette des le\u00e7ons",
    "Click Add to specify Module Label": "Cliquez sur \u00ab\u00a0Ajouter\u00a0\u00bb pour sp\u00e9cifier l\u2019\u00e9tiquette du module",
    "Click Add to specify Modules Label": "Cliquez sur \u00ab\u00a0Ajouter\u00a0\u00bb pour sp\u00e9cifier l\u2019\u00e9tiquette des modules",
    "Click to choose all %s at once.": "Cliquez pour choisir tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "Click to remove all chosen %s at once.": "Cliquez pour enlever tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "Cohort": "Division",
    "Cohort Comp.": "Comp. de la division",
    "Company": "Soci\u00e9t\u00e9",
    "Company Admin": "Admin soci\u00e9t\u00e9",
    "Company ID": "Identifiant de la soci\u00e9t\u00e9",
    "Company doesn't exist! ": "La soci\u00e9t\u00e9 n\u2019existe pas\u00a0!",
    "Complete": "Termin\u00e9",
    "Complete all content to continue": "Compl\u00e9ter l\u2019ensemble du contenu pour continuer",
    "Complete all content to continue.": "Compl\u00e9ter l\u2019ensemble du contenu pour continuer",
    "Completed": "Termin\u00e9",
    "Contains Errors": "Contient des erreurs",
    "Content is complete, please continue.": "Le contenu est complet\u00a0; veuillez continuer",
    "Couldn't add tag to course!": "Impossible d\u2019ajouter une \u00e9tiquette au cours\u00a0!",
    "Couldn't create new company!": "Impossible de cr\u00e9er une nouvelle soci\u00e9t\u00e9\u00a0!",
    "Couldn't create new tag!": "Impossible de cr\u00e9er une nouvelle \u00e9tiquette\u00a0!",
    "Couldn't delete tag!": "Impossible de supprimer l\u2019\u00e9tiquette\u00a0!",
    "Couldn't delink App!": "Impossible de d\u00e9lier cette application\u00a0!",
    "Couldn't link this App!": "Impossible de lier cette application\u00a0!",
    "Country": "Pays",
    "Course": "Cours",
    "Course ID": "Identifiant du cours",
    "Course Name": "Nom du cours",
    "Dashboard Name": "Nom du tableau de bord",
    "Date Added": "Date ajout\u00e9e",
    "December": "D\u00e9cembre",
    "Delete Role": "Supprimer le r\u00f4le",
    "Deployment Mech": "M\u00e9canisme de d\u00e9ploiement",
    "Digital Content": "Cours num\u00e9rique",
    "Digital Course": "Cours num\u00e9rique",
    "Discussion": "Discussions",
    "Do you really want to delete: \n": "Voulez-vous vraiment supprimer\u00a0: \n",
    "Download": "T\u00e9l\u00e9charger",
    "Download CSV File": "T\u00e9l\u00e9charger un fichier CSV",
    "Download Notifications CSV": "Notification de t\u00e9l\u00e9chargement CSV",
    "Email": "E-mail",
    "Email Preview Success!": "Aper\u00e7u d\u2019e-mail valid\u00e9\u00a0!",
    "Email Success!": "E-mail valid\u00e9 !",
    "Email can't be empty! ": "L\u2019e-mail ne peut pas \u00eatre vide\u00a0!",
    "End": "Terminer",
    "End Date": "Date de fin",
    "End time": "Heure de fin",
    "Engagement": "Implication",
    "Enroll Participant": "Inscrire le participant",
    "Enroll Participants": "Inscrire les participants",
    "Enroll this list in another course": "Inscrire cette liste dans un autre cours",
    "Enrolled In": "Inscrit \u00e0",
    "Error File": "Fichier d\u2019erreur",
    "Error Occured!": "Une erreur s\u2019est produite\u00a0!",
    "Error initiating the report generation. Please retry later.": "Erreur d\u2019initiation de g\u00e9n\u00e9ration de rapport. Veuillez r\u00e9essayer plus tard.",
    "Error processing CSV file.": "Erreur de traitement du fichier CSV.",
    "Error uploading file. Please try again and be sure to use an accepted file format.": "Erreur pendant le t\u00e9l\u00e9chargement du fichier. Veuillez r\u00e9essayer et vous assurer d\u2019utiliser un format de fichier accept\u00e9.",
    "Export Report": "Exporter le rapport",
    "Exporting Stats for All Users": "Exportation des statistiques pour tous les utilisateurs",
    "February": "F\u00e9vrier",
    "Female": "Femme",
    "Fetching data for file: %(filename)s": "R\u00e9cup\u00e9ration des donn\u00e9es pour le fichier\u00a0: %(filename)s",
    "File name": "Nom de fichier",
    "File successfully uploaded!": "Fichier t\u00e9l\u00e9charg\u00e9 avec succ\u00e8s\u00a0!",
    "Filename": "Nom du fichier",
    "Filter": "Filtrer",
    "First name can't be empty! ": "Le pr\u00e9nom ne peut pas \u00eatre vide\u00a0!",
    "Go to %(course_id)s Course": "Aller au cours %(course_id)s",
    "Grade": "Note",
    "Group Work": "Travail de groupe",
    "Group Work: %(label)s": "Travail de groupe\u00a0: %(label)s",
    "Group successfully updated": "Groupe actualis\u00e9 avec succ\u00e8s",
    "Group was not created": "Le groupe n\u2019a pas \u00e9t\u00e9 cr\u00e9\u00e9",
    "Group work": "Travail de groupe",
    "Hide": "Masquer",
    "Hide Details": "Cacher les d\u00e9tails",
    "Hide password": "Masquer le mot de passe",
    "I'm Done": "J\u2019ai termin\u00e9",
    "Importing %(processed)s of %(total)s rows": "Importation de %(processed)s lignes sur (%(total)s",
    "Importing..": "Importation..",
    "In Person Session": "Session en t\u00eate-\u00e0-t\u00eate",
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "Inclure la r\u00e9partition des progression pour chaque le\u00e7on (remarque\u00a0: l\u2019exportation prendra plus de temps)",
    "Incomplete": "Inachev\u00e9",
    "Initiated by": "Initi\u00e9 par",
    "Invalid format for CSV file.": "Format non valide pour le fichier CSV.",
    "It looks like you're not active. Click OK to keep working.": "Il semblerait que vous n\u2019\u00eates pas actif. Cliquez sur OK pour continuer \u00e0 travailler.",
    "It looks like your browser settings has pop-ups disabled.": "Il semblerait que les fen\u00eatres contextuelles soient d\u00e9sactiv\u00e9es dans les param\u00e8tres de votre navigateur.",
    "January": "Janvier",
    "July": "Juillet",
    "June": "Juin",
    "Last Log In": "Derni\u00e8re connexion",
    "Last name can't be empty! ": "Le nom de famille ne peut pas \u00eatre vide\u00a0!",
    "Launch pop-up to continue": "Lancez la fen\u00eatre contextuelle pour continuer",
    "Leaderboards": "Classements",
    "Learner email": "E-mail de l\u2019apprenant",
    "Lesson": "Le\u00e7on",
    "Male": "Homme",
    "Manager email": "E-mail du gestionnaire",
    "March": "Mars",
    "May": "Mai",
    "Midnight": "Minuit",
    "Moderator": "Mod\u00e9rateur",
    "Module": "Module",
    "Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.": "Il doit contenir au moins 8 caract\u00e8res et inclure des minuscules et des majuscules, plus des nombres ou des caract\u00e8res sp\u00e9ciaux.",
    "Name": "Nom",
    "No App Display Name!": "Aucun nom d\u2019affichage d\u2019application",
    "No Company Display Name!": "Aucun nom d\u2019affichage de soci\u00e9t\u00e9\u00a0!",
    "No file Selected": "Aucun fichier s\u00e9lectionn\u00e9",
    "No. of Courses": "N\u00b0 des cours",
    "No. of Participants": "N\u00b0 des participants",
    "NoName": "Aucun nom",
    "None": "Aucun",
    "Noon": "Midi",
    "Note: You are %s hour ahead of server time.": [
      "Note\u00a0: l'heure du serveur pr\u00e9c\u00e8de votre heure de %s heure.",
      "Note\u00a0: l'heure du serveur pr\u00e9c\u00e8de votre heure de %s heures."
    ],
    "Note: You are %s hour behind server time.": [
      "Note\u00a0: votre heure pr\u00e9c\u00e8de l'heure du serveur de %s heure.",
      "Note\u00a0: votre heure pr\u00e9c\u00e8de l'heure du serveur de %s heures."
    ],
    "Notification": "Notification",
    "November": "Novembre",
    "Now": "Maintenant",
    "Observer": "Observateur",
    "October": "Octobre",
    "Only alphanumeric characters and spaces allowed": "Seuls les caract\u00e8res alphanum\u00e9riques et les espaces sont autoris\u00e9s",
    "Participant": "Participant",
    "Participants": "Participants",
    "Please enter new template name!": "Saisissez le nom du nouveau mod\u00e8le\u00a0!",
    "Please enter preview email!": "Veuillez saisir l\u2019e-mail de pr\u00e9visualisation\u00a0!",
    "Please enter updated template name or leave the old one!": "Saisissez le nom du mod\u00e8le actualis\u00e9 ou laissez le nom de l\u2019ancien mod\u00e8le !",
    "Please select at least one course": "S\u00e9lectionnez au moins un cours",
    "Please select at least one student": "S\u00e9lectionnez au moins un \u00e9tudiant",
    "Please select file first.": "Veuillez d\u2019abord s\u00e9lectionner un fichier.",
    "Please select file for upload.": "S\u00e9lectionnez le fichier \u00e0 t\u00e9l\u00e9charger.",
    "Please select project": "S\u00e9lectionnez votre projet",
    "Poll/Survey Question": "Question du sondage/de l\u2019enqu\u00eate",
    "Preview Email!": "Pr\u00e9visualiser l\u2019e-mail\u00a0!",
    "Proficiency": "Comp\u00e9tence",
    "Program": "Programme",
    "Progress": "Progression",
    "Progress : 0%": "Progression\u00a0: 0\u00a0%",
    "Progress: %(progress)s %": "Progression\u00a0: %(progress)s %",
    "Progress: %(value)s%": "Progression\u00a0: %(value)s%",
    "Remove": "Enlever",
    "Remove all": "Tout enlever",
    "Report of bulk update will be sent to your email.": "Le rapport de la mise \u00e0 jour group\u00e9e sera envoy\u00e9 \u00e0 votre e-mail.",
    "Request Time": "Dur\u00e9e de la requ\u00eate",
    "Save Changes": "Enregistrer les modifications",
    "Search by Keyword": "Rechercher par mot-cl\u00e9",
    "Select Course": "S\u00e9lectionner le cours",
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "S\u00e9lectionn\u00e9\u00a0: %(selected)s, Valid\u00e9\u00a0: %(successful)s, Non valid\u00e9\u00a0: %(failed)s",
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "S\u00e9lectionn\u00e9\u00a0: %(selectedRows)s, Valid\u00e9\u00a0: 0, Non valid\u00e9\u00a0: 0",
    "Send": "Envoyer",
    "Send Course Intro Email": "Envoyer l\u2019e-mail de pr\u00e9sentation du cours",
    "September": "Septembre",
    "Show": "Afficher",
    "Show Errors": "Afficher les erreurs",
    "Show password": "Afficher le mot de passe",
    "Start": "D\u00e9marrer",
    "Start time": "Heure de d\u00e9but",
    "Status": "Statut",
    "Successful": "R\u00e9ussie",
    "Successfully Enrolled in 1 Course": "Vous \u00eates maintenant inscrit \u00e0 1 cours.",
    "Successfully added new template!": "Nouveau mod\u00e8le ajout\u00e9 avec succ\u00e8s\u00a0!",
    "Successfully deleted template!": "Mod\u00e8le supprim\u00e9 avec succ\u00e8s\u00a0!",
    "Successfully sent email!": "E-mail envoy\u00e9 avec succ\u00e8s\u00a0!",
    "Successfully sent preview email!": "E-mail d\u2019aper\u00e7u envoy\u00e9 avec succ\u00e8s\u00a0!",
    "Successfully updated template!": "Mod\u00e8le mis \u00e0 jour avec succ\u00e8s\u00a0!",
    "TA": "AF",
    "Task failed to execute. Please retry later.": "Impossible d\u2019ex\u00e9cuter la t\u00e2che. Veuillez r\u00e9essayer plus tard.",
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "Le fichier .csv contient plusieurs lignes %(limit)s\u00a0: %(lines)s, divisez les lignes en plusieurs fichiers\u00a0!",
    "The content takes place in a new window.": "Le contenu s\u2019affiche dans une nouvelle fen\u00eatre.",
    "There was an error submitting your file.": "Une erreur s\u2019est produite lors de l\u2019envoi de votre fichier.",
    "This app name cannot contain non-alphanumeric characters!": "Le nom de cette application ne peut contenir que des caract\u00e8res alphanum\u00e9riques\u00a0!",
    "This app name cannot have more than 30 characters!": "Le nom de l\u2019application ne peut pas contenir plus de 30\u00a0caract\u00e8res\u00a0!",
    "This company name cannot contain non-alphanumeric characters!": "Le nom de la soci\u00e9t\u00e9 ne peut contenir que des caract\u00e8res alphanum\u00e9riques\u00a0!",
    "This company name cannot have more than 30 characters!": "Le nom de la soci\u00e9t\u00e9 ne peut pas contenir plus de 30\u00a0caract\u00e8res\u00a0!",
    "This field is required.": "Ce champ est requis.",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Ceci est une liste des \u00ab\u00a0%s\u00a0\u00bb disponibles. Vous pouvez en choisir en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab\u00a0Choisir\u00a0\u00bb entre les deux zones.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Ceci est la liste des \u00ab\u00a0%s\u00a0\u00bb choisi(e)s. Vous pouvez en enlever en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab Enlever \u00bb entre les deux zones.",
    "This tag name cannot contain non-alphanumeric characters!": "Le nom de cette \u00e9tiquette ne peut contenir que des caract\u00e8res alphanum\u00e9riques\u00a0!",
    "This tag name cannot have more than 30 characters!": "Le nom de l\u2019\u00e9tiquette ne peut pas contenir plus de 30\u00a0caract\u00e8res\u00a0!",
    "Today": "Aujourd'hui",
    "Today at ": "aujourd'hui",
    "Tomorrow": "Demain",
    "Try selecting your company from the type-ahead results.": "Essayez de s\u00e9lectionner votre soci\u00e9t\u00e9 parmi les r\u00e9sultats de pr\u00e9-saisie.",
    "Type into this box to filter down the list of available %s.": "\u00c9crivez dans cette zone pour filtrer la liste des \u00ab\u00a0%s\u00a0\u00bb disponibles.",
    "Unenroll": "D\u00e9sinscrire",
    "Unenroll Participants": "D\u00e9sinscrire les participants",
    "Unenroll all selected participants from this course?": "D\u00e9sinscrire tous les participants s\u00e9lectionn\u00e9s de ce cours\u00a0?",
    "Updated user data!": "Donn\u00e9es d\u2019utilisateur actualis\u00e9es\u00a0!",
    "Urban Airship URL": "Urban Airship URL",
    "User successfully enrolled in course": "Utilisateur inscrit au cours avec succ\u00e8s",
    "User will be enrolled in course selected below.": "L\u2019utilisateur sera inscrit au cours s\u00e9lectionn\u00e9 ci-dessous.",
    "Username": "Nom d\u2019utilisateur",
    "Username can't be empty! ": "Le nom d\u2019utilisateur ne peut pas \u00eatre vide\u00a0!",
    "View Details": "Voir les d\u00e9tails",
    "We'll e-mail you when your report is ready to download.": "Nous vous enverrons un e-mail lorsque le t\u00e9l\u00e9chargement de votre rapport sera pr\u00eat.",
    "Webinar": "Webinaire",
    "Welcome to McKinsey Academy": "Bienvenue \u00e0 McKinsey Academy",
    "What would you like to do now?": "Que d\u00e9sirez-vous faire maintenant\u00a0?",
    "Yesterday": "Hier",
    "You are about to delete email template. Are you sure?": "\u00cates-vous s\u00fbr\u00a0 de vouloir supprimer le mod\u00e8le d\u2019e-mail\u00a0?",
    "You are now": "Vous \u00eates maintenant",
    "You can only add up to 4 fields": "Vous ne pouvez ajouter que 4 champs",
    "You don't have permission to create a new tag, please select one from the list!": "Vous n\u2019avez pas l\u2019autorisation de cr\u00e9er une nouvelle \u00e9tiquette, s\u00e9lectionnez-en une dans la liste\u00a0!",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Vous avez s\u00e9lectionn\u00e9 une action, et vous n'avez fait aucune modification sur des champs. Vous cherchez probablement le bouton Envoyer et non le bouton Enregistrer.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Vous avez s\u00e9lectionn\u00e9 une action, mais vous n'avez pas encore sauvegard\u00e9 certains champs modifi\u00e9s. Cliquez sur OK pour sauver. Vous devrez r\u00e9appliquer l'action.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Vous avez des modifications non sauvegard\u00e9es sur certains champs \u00e9ditables. Si vous lancez une action, ces modifications vont \u00eatre perdues.",
    "You need to enter course ID!": "Vous devez saisir un identifiant de cours\u00a0!",
    "You need to enter name!": "Vous devez saisir un nom\u00a0!",
    "You need to select at least one participant to be able to apply bulk actions.": "Vous devez s\u00e9lectionner au moins un participant pour pouvoir appliquer les actions en lot.",
    "You need to select course!": "Vous devez s\u00e9lectionner un cours\u00a0!",
    "You need to select status!": "Vous devez s\u00e9lectionner un statut\u00a0!",
    "You were logged out due to inactivity. Please log back in to continue.": "Vous avez \u00e9t\u00e9 d\u00e9connect\u00e9 pour cause d\u2019inactivit\u00e9. Veuillez vous reconnecter pour continuer.",
    "Your Progress: %(value)s%": "Votre progression\u00a0: %(value)s%",
    "Your course begins in %(days)s day.": [
      "Votre cours commence dans %(days)s jour.",
      "Votre cours commence dans %(days)s jours."
    ],
    "Your course hasn't begun yet. ": "Votre cours n\u2019a pas encore commenc\u00e9.",
    "complete": "termin\u00e9",
    "contains %s learner": [
      "contient %s apprenant",
      "contient %s apprenants"
    ],
    "course id": "identifiant de cours",
    "email": "e-mail",
    "for": "pour",
    "iOS DL URL": "iOS DL URL",
    "in the cohort!": "dans le groupe!",
    "location": "emplacement",
    "one letter Friday\u0004F": "V",
    "one letter Monday\u0004M": "L",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "J",
    "one letter Tuesday\u0004T": "M",
    "one letter Wednesday\u0004W": "M",
    "same as your organization's average": "identique \u00e0 la moyenne de votre organisation",
    "status": "statut"
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
    "DATETIME_FORMAT": "j F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%Y",
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%d.%m.%Y",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j N Y H:i",
    "SHORT_DATE_FORMAT": "j N Y",
    "THOUSAND_SEPARATOR": "\u00a0",
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

