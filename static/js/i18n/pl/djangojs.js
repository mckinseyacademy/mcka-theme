

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
    " day": " dzie\u0144",
    " week": " tydzie\u0144",
    "# of people": "# ludzi",
    "% total cohort": "% ca\u0142kowitej liczby kursant\u00f3w",
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s Kurs otagowany za pomoc\u0105 %(tagDetails)s",
      "%(count)s Kursy otagowany za pomoc\u0105 %(tagDetails)s"
    ],
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s Wykorzystaj czas pozosta\u0142y do rozpocz\u0119cia kursu, aby lepiej zapozna\u0107 si\u0119 z nasz\u0105 stron\u0105 i przygotowa\u0107 si\u0119 na czekaj\u0105ce Ci\u0119 do\u015bwiadczenia.",
    "%(sel)s of %(cnt)s selected": [
      "Wybrano %(sel)s z %(cnt)s",
      "Wybrano %(sel)s z %(cnt)s"
    ],
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "%(selectedRows)s Uczestnicy zostan\u0105 zarejestrowani na kurs wybrany poni\u017cej.",
      "%(selectedRows)s Uczestnik zostanie zarejestrowany na kurs wybrany poni\u017cej."
    ],
    "%(value)s%": "%(value)s%",
    "%s invalid email was ignored.": [
      "%s nieprawid\u0142owy e-mail zosta\u0142 zignorowany.",
      "%s nieprawid\u0142owych e-maili zosta\u0142o zignorowanych."
    ],
    "%s learner has been added to this cohort.": [
      "%s ucze\u0144 zosta\u0142 dodany do tej grupy kursant\u00f3w.",
      "%s uczni\u00f3w zosta\u0142o dodanych do tej grupy kursant\u00f3w."
    ],
    "%s learner has been moved to this cohort.": [
      "%s ucze\u0144 zosta\u0142 przeniesiony do tej grupy kursant\u00f3w.",
      "%s uczni\u00f3w zosta\u0142o przeniesionych do tej grupy kursant\u00f3w."
    ],
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "%s ucze\u0144 zosta\u0142 wst\u0119pnie dodany do tej grupy kursant\u00f3w. Po zarejestrowaniu si\u0119, ucze\u0144 ten zostanie automatycznie dodany do grupy kursant\u00f3w.",
      "%s uczni\u00f3w zosta\u0142o wst\u0119pnie dodanych do tej grupy kursant\u00f3w. Po zarejestrowaniu si\u0119, ucze\u0144 ten zostanie automatycznie dodany do grupy kursant\u00f3w."
    ],
    "%s user was already in this cohort.": [
      "%s u\u017cytkownik jest ju\u017c w tej grupie kursant\u00f3w.",
      "%s u\u017cytkownik\u00f3w jest ju\u017c w tej grupie kursant\u00f3w."
    ],
    "%s user/email was not found.": [
      "%s u\u017cytkownik/adres e-mail nie zosta\u0142 odnaleziony.",
      "%s u\u017cytkownik\u00f3w/adres\u00f3w e-mail nie zosta\u0142o odnalezionych."
    ],
    ".0%": "0%",
    "2 or more fields can not have the same name": "2 lub wi\u0119cej p\u00f3l nie mog\u0105 mie\u0107 takiej samej nazwy",
    "6 a.m.": "6 rano",
    "6 p.m.": "6 po po\u0142udniu",
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "<span class=\"green\"> %(diff)s point</span> powy\u017cej \u015bredniej Twojej organizacji",
      "<span class=\"green\"> %(diff)s points</span> powy\u017cej \u015bredniej Twojej organizacji"
    ],
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "<span class=\"green\">%(diff)s% </span> powy\u017cej \u015bredniej Twojej organizacji",
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "<span class=\"red\"> %(diff)s point</span> poni\u017cej \u015bredniej Twojej organizacji",
      "<span class=\"red\"> %(diff)s points</span> poni\u017cej \u015bredniej Twojej organizacji"
    ],
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "<span class=\"red\"> %(diff)s% </span> poni\u017cej \u015bredniej Twojej organizacji",
    "Activated": "Aktywowano",
    "Activation File": "Plik aktywacyjny",
    "Activation Link": "Link aktywacyjny",
    "Active": "Aktywny",
    "Add new role e.g CEO,CTO": "Dodaj nowe stanowisko/rol\u0119 np. CEO,CTO",
    "Admin Company": "Firma administratora",
    "Admin Permissions": "Uprawnienia dost\u0119pu administratora",
    "All students added to private group have to be members of same company.": "Wszyscy uczniowie dodani do grupy prywatnej musz\u0105 by\u0107 cz\u0142onkami tej samej firmy.",
    "An error occurred submitting the request.": "Podczas wysy\u0142ania \u017c\u0105dania wyst\u0105pi\u0142 b\u0142\u0105d.",
    "Analytics URL": "Adres URL dla analizy i statystyk",
    "Android DL URL": "Android DL URL",
    "App Name": "Nazwa aplikacji",
    "April": "Kwiecie\u0144",
    "Are you sure you want to remove this ?": "Czy na pewno chcesz usun\u0105\u0107 ?",
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "Czy jeste\u015b pewny, \u017ce chcesz usun\u0105\u0107 t\u0119 grup\u0119? Spowoduje to usuni\u0119cie wszelkich przes\u0142anych plik\u00f3w i informacji zwrotnych powi\u0105zanych z grup\u0105.",
    "Are you sure?": "Czy jeste\u015b pewny?",
    "Assessment: %(label)s": "Ocena: %(label)s",
    "August": "Sierpie\u0144",
    "Available %s": "Dost\u0119pne %s",
    "Avg Progress": "\u015aredni stopie\u0144 uko\u0144czenia",
    "Business Function": "Funkcja biznesowa",
    "Business Unit": "Jednostka biznesowa",
    "Cancel": "Anuluj",
    "Change Status": "Zmie\u0144 status",
    "Change status of all selected participants to:": "Zmie\u0144 status wybranych uczestnik\u00f3w na:",
    "Check for Completion": "Sprawd\u017a pod k\u0105tem wype\u0142nienia",
    "Choose": "Wybierz",
    "Choose a Date": "Wybierz Dat\u0119",
    "Choose a Time": "Wybierz Czas",
    "Choose a time": "Wybierz czas",
    "Choose all": "Wybierz wszystkie",
    "Chosen %s": "Wybrane %s",
    "Click Add to specify Lesson Label": "Kliknij \u201eDodaj\u201d, aby okre\u015bli\u0107 Etykiet\u0119 lekcji",
    "Click Add to specify Lessons Label": "Kliknij \u201eDodaj\u201d, aby okre\u015bli\u0107 Etykiet\u0119 lekcji",
    "Click Add to specify Module Label": "Kliknij \u201eDodaj\u201d, aby okre\u015bli\u0107 Etykiet\u0119 modu\u0142u",
    "Click Add to specify Modules Label": "Kliknij \u201eDodaj\u201d, aby okre\u015bli\u0107 Etykiet\u0119 modu\u0142\u00f3w",
    "Click to choose all %s at once.": "Kliknij, aby wybra\u0107 jednocze\u015bnie wszystkie %s.",
    "Click to remove all chosen %s at once.": "Kliknij, aby usun\u0105\u0107 jednocze\u015bnie wszystkie wybrane %s.",
    "Cohort": "Grupa kursant\u00f3w",
    "Cohort Comp.": "Firma tej grupy kursa",
    "Company": "Firma",
    "Company Admin": "Administrator firmy",
    "Company ID": "Numer ID firmy",
    "Company doesn't exist! ": "Firma nie istnieje!",
    "Complete": "Uko\u0144czono",
    "Complete all content to continue": "Prosimy wype\u0142ni\u0107 ca\u0142\u0105 zawarto\u015b\u0107, aby kontynuowa\u0107",
    "Complete all content to continue.": "Prosimy wype\u0142ni\u0107 ca\u0142\u0105 zawarto\u015b\u0107, aby kontynuowa\u0107",
    "Completed": "Uko\u0144czono",
    "Contains Errors": "Zawiera b\u0142\u0119dy",
    "Content is complete, please continue.": "Zawarto\u015b\u0107 jest wype\u0142niona, prosimy kontynuowa\u0107",
    "Couldn't add tag to course!": "Nie mo\u017cna doda\u0107 tagu do kursu",
    "Couldn't create new company!": "Nie mo\u017cna utworzy\u0107 firmy!",
    "Couldn't create new tag!": "Nie mo\u017cna utworzy\u0107 nowego tagu!",
    "Couldn't delete tag!": "Nie mo\u017cna usun\u0105\u0107 tagu",
    "Couldn't delink App!": "Nie mo\u017cna od\u0142\u0105czy\u0107 tej aplikacji!",
    "Couldn't link this App!": "Nie mo\u017cna pod\u0142\u0105czy\u0107 tej aplikacji!",
    "Country": "Kraj",
    "Course": "Kurs",
    "Course ID": "Numer identyfikacyjny kursu",
    "Course Name": "Nazwa kursu",
    "Dashboard Name": "Nazwa panelu",
    "Date Added": "Data dodania",
    "December": "Grudzie\u0144",
    "Delete Role": "Usu\u0144 stanowisko/rol\u0119",
    "Deployment Mech": "Mechanizm wdro\u017cenia",
    "Digital Content": "Zawarto\u015b\u0107 cyfrowa",
    "Digital Course": "Kurs cyfrowy",
    "Do you really want to delete: \n": "Czy na pewno chcesz usun\u0105\u0107: \n",
    "Download": "Pobierz",
    "Download CSV File": "Pobierz plik CSV",
    "Download Notifications CSV": "Pobierz powiadomienia CSV",
    "Downloadable Workgroup Completion Report": "Raport o uko\u0144czeniu zada\u0144 grupowych w wersji do pobrania",
    "Email": "E-mail",
    "Email Preview Success!": "Pomy\u015blnie wys\u0142ano e-mail wst\u0119pny!",
    "Email Success!": "Pomy\u015blnie wys\u0142ano e-mail!",
    "Email can't be empty! ": "Adres e-mail nie mo\u017ce by\u0107 pusty!",
    "End": "Koniec",
    "End Date": "Data uko\u0144czenia",
    "End time": "Czas zako\u0144czenia",
    "Engagement": "Poziom zaanga\u017cowania",
    "Enroll Participant": "Zarejestruj uczestnika",
    "Enroll Participants": "Zarejestruj uczestnik\u00f3w",
    "Enroll this list in another course": "Zarejestruj t\u0119 list\u0119 na inny kurs",
    "Enrolled In": "Zarejestrowany",
    "Error File": "Plik b\u0142\u0119du",
    "Error Occured!": "Wyst\u0105pi\u0142 b\u0142\u0105d!",
    "Error initiating the report generation. Please retry later.": "Podczas pr\u00f3by wygenerowania reportu wyst\u0105pi\u0142 b\u0142\u0105d. Spr\u00f3buj p\u00f3\u017aniej.",
    "Error processing CSV file.": "B\u0142\u0105d przetwarzania pliku CSV.",
    "Error uploading file. Please try again and be sure to use an accepted file format.": "Nie uda\u0142o si\u0119 przes\u0142a\u0107 pliku. Sprawd\u017a, czy format pliku jest poprawny i spr\u00f3buj ponownie.",
    "Export Report": "Wyeksportuj raport",
    "Exporting Stats for All Users": "Eksportowanie statystyk dla wszystkich uczestnik\u00f3w",
    "February": "Luty",
    "Female": "Kobieta",
    "Fetching data for file: %(filename)s": "Pobieranie danych dla pliku: %(filename)s",
    "File name": "Nazwa pliku",
    "File successfully uploaded!": "Plik przes\u0142any pomy\u015blnie",
    "Filename": "Nazwa pliku",
    "Filter": "Filtr",
    "First name can't be empty! ": "Imi\u0119 nie mo\u017ce by\u0107 puste!",
    "Go to %(course_id)s Course": "Przejd\u017a do kursu %(course_id)s",
    "Grade": "Ocena",
    "Group Work: %(label)s": "Praca grupowa: %(label)s",
    "Group successfully updated": "Grupa zaktualizowana prawid\u0142owo",
    "Group was not created": "Grupa nie zosta\u0142a utworzona",
    "Group work": "Praca grupowa",
    "Hide": "Ukryj",
    "Hide Details": "Ukryj szczeg\u00f3\u0142y",
    "Hide password": "Ukryj has\u0142o",
    "I'm Done": "Sko\u0144czy\u0142em",
    "Importing %(processed)s of %(total)s rows": "Trwa importowanie %(processed)s z %(total)s wierszy",
    "Importing..": "Trwa importowanie..",
    "In Person Session": "Sesja na \u017cywo",
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "Uwzgl\u0119dnij zestawienie stopnia uko\u0144czenia dla ka\u017cdej lekcji z osobna (Uwaga: eksport zajmie wi\u0119cej czasu)",
    "Incomplete": "Nie uko\u0144czono",
    "Initiated by": "Zainicjowany przez",
    "Invalid format for CSV file.": "Nieprawid\u0142owy format pliku CSV.",
    "It looks like you're not active. Click OK to keep working.": "Wygl\u0105da na to, \u017ce jeste\u015b nieaktywny. Wci\u015bnij OK, aby kontynuowa\u0107 prac\u0119.",
    "It looks like your browser settings has pop-ups disabled.": "Wygl\u0105da na to, \u017ce Twoja przegl\u0105darka blokuje wyskakuj\u0105ce okienka.",
    "January": "Stycze\u0144",
    "July": "Lipiec",
    "June": "Czerwiec",
    "Last Log In": "Ostatnie logowanie",
    "Last name can't be empty! ": "Nazwisko nie mo\u017ce by\u0107 puste!",
    "Launch pop-up to continue": "W\u0142\u0105cz obs\u0142ug\u0119 wyskakuj\u0105cych okienek, aby kontynuowa\u0107",
    "Learner email": "Adres e-mail ucznia",
    "Lesson": "Lekcja",
    "Male": "M\u0119\u017cczyzna",
    "Manager email": "Adres e-mail mened\u017cera",
    "March": "Marzec",
    "May": "Maj",
    "Midnight": "P\u00f3\u0142noc",
    "Moderator": "Moderator",
    "Module": "Modu\u0142",
    "Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.": "Musi sk\u0142ada\u0107 si\u0119 z przynajmniej 8 znak\u00f3w i zawiera\u0107 co najmniej jedn\u0105 ma\u0142\u0105 liter\u0119, jedn\u0105 wielk\u0105 liter\u0119 oraz jedn\u0105 cyfr\u0119 lub znak specjalny.",
    "Name": "Nazwa",
    "No App Display Name!": "Brak publicznej nazwy aplikacji!",
    "No Company Display Name!": "Brak publicznej nazwy firmy",
    "No file Selected": "Nie wybrano pliku.",
    "No. of Courses": "Liczba kurs\u00f3w",
    "No. of Participants": "Liczba uczestnik\u00f3w",
    "NoName": "NoName",
    "None": "\u017badne",
    "Noon": "Po\u0142udnie",
    "Note: You are %s hour ahead of server time.": [
      "Uwaga: Czas lokalny jest przesuni\u0119ty o %s godzin\u0119 do przodu w stosunku do czasu serwera.",
      "Uwaga: Czas lokalny jest przesuni\u0119ty o %s godziny do przodu w stosunku do czasu serwera."
    ],
    "Note: You are %s hour behind server time.": [
      "Uwaga: Czas lokalny jest przesuni\u0119ty o %s godzin\u0119 do ty\u0142u w stosunku do czasu serwera.",
      "Uwaga: Czas lokalny jest przesuni\u0119ty o %s godziny do ty\u0142u w stosunku do czasu serwera."
    ],
    "Notification": "Powiadomienia",
    "November": "Listopad",
    "Now": "Teraz",
    "Observer": "Obserwator",
    "October": "Pa\u017adziernik",
    "Only alphanumeric characters and spaces allowed": "Dozwolone s\u0105 tylko znaki alfanumeryczne i spacje",
    "Participant": "Uczestnik",
    "Participants": "Uczestnicy",
    "Please enter new template name!": "Wprowad\u017a nazw\u0119 nowego szablonu",
    "Please enter preview email!": "Wprowad\u017a e-mail wst\u0119pny",
    "Please enter updated template name or leave the old one!": "Wprowad\u017a zaktualizowan\u0105 nazw\u0119 szablonu lub pozostaw poprzedni\u0105",
    "Please select at least one course": "Nale\u017cy wybra\u0107 przynajmniej jeden kurs.",
    "Please select at least one student": "Nale\u017cy wybra\u0107 przynajmniej jednego ucznia",
    "Please select file first.": "Prosimy najpierw wybra\u0107 plik.",
    "Please select file for upload.": "Prosimy najpierw wybra\u0107 plik.",
    "Please select project": "Prosimy wybra\u0107 projekt",
    "Poll/Survey Question": "Pytanie sonda\u017cu/ankiety",
    "Preview Email!": "E-mail wst\u0119pny!",
    "Proficiency": "Bieg\u0142o\u015b\u0107",
    "Program": "Program",
    "Progress": "Stopie\u0144 uko\u0144czenia",
    "Progress : 0%": "Stopie\u0144 uko\u0144czenia: 0%",
    "Progress: %(progress)s %": "Stopie\u0144 uko\u0144czenia: %(progress)s %",
    "Progress: %(value)s%": "Stopie\u0144 uko\u0144czenia: %(value)s%",
    "Remove": "Usu\u0144",
    "Remove all": "Usu\u0144 wszystkie",
    "Report of bulk update will be sent to your email.": "Raport z aktualizacji masowej zostanie wys\u0142any na Tw\u00f3j adres e-mail.",
    "Request Time": "Czas \u017c\u0105dania",
    "Save Changes": "Zapisz zmiany",
    "Search by Keyword": "Wyszukaj za pomoc\u0105 s\u0142owa kluczowych",
    "Select Course": "Wybierz kurs",
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "Wybranych: %(selected)s, Uko\u0144czy\u0142o pomy\u015blnie: %(successful)s, Nie uko\u0144czy\u0142o: %(failed)s",
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "Wybranych: %(selectedRows)s, Uko\u0144czy\u0142o pomy\u015blnie: 0, Nie uko\u0144czy\u0142o: 0",
    "Send": "Wy\u015blij",
    "Send Course Intro Email": "Wy\u015blij wiadomo\u015b\u0107 e-mail ze wst\u0119pem do kursu",
    "September": "Wrzesie\u0144",
    "Show": "Poka\u017c",
    "Show Errors": "Poka\u017c b\u0142\u0119dy",
    "Show password": "Poka\u017c has\u0142o",
    "Start": "Start",
    "Start time": "Czas rozpocz\u0119cia",
    "Status": "Status",
    "Successful": "Zako\u0144czono powodzeniem",
    "Successfully Enrolled in 1 Course": "Uda\u0142o si\u0119 zarejestrowa\u0107 Ci\u0119 na 1 kurs.",
    "Successfully added new template!": "Pomy\u015blnie dodano nowy szablon",
    "Successfully deleted template!": "Pomy\u015blnie usuni\u0119to szablon",
    "Successfully sent email!": "Pomy\u015blnie wys\u0142ano wiadomo\u015b\u0107 e-mail!",
    "Successfully sent preview email!": "Pomy\u015blnie wys\u0142ano e-mail wst\u0119pny!",
    "Successfully updated template!": "Pomy\u015blnie zaktualizowano szablon",
    "TA": "Asystent kursu",
    "Task failed to execute. Please retry later.": "Nie uda\u0142o si\u0119 wykona\u0107 zadania. Spr\u00f3buj p\u00f3\u017aniej.",
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "Pliki .csv nie mo\u017ce zawiera\u0107 wi\u0119cej ni\u017c %(limit)s wierszy: %(lines)s , prosimy podzieli\u0107 go na wi\u0119cej plik\u00f3w!",
    "The content takes place in a new window.": "Ta zawarto\u015b\u0107 musi zosta\u0107 otwarta w nowym oknie.",
    "There was an error submitting your file.": "Podczas przesy\u0142ania Twojego pliku wyst\u0105pi\u0142 b\u0142\u0105d.",
    "This app name cannot contain non-alphanumeric characters!": "Nazwa tej aplikacji mo\u017ce posiada\u0107 jedynie znaki alfanumeryczne",
    "This app name cannot have more than 30 characters!": "Nazwa tej aplikacji nie mo\u017ce przekroczy\u0107 30 znak\u00f3w",
    "This company name cannot contain non-alphanumeric characters!": "Nazwa firmy mo\u017ce posiada\u0107 jedynie znaki alfanumeryczne",
    "This company name cannot have more than 30 characters!": "Nazwa firmy nie mo\u017ce przekroczy\u0107 30 znak\u00f3w",
    "This field is required.": "To pole jest wymagane.",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "To lista dost\u0119pnych %s. Aby wybra\u0107 pozycje, zaznacz je i kliknij strza\u0142k\u0119 \u201eWybierz\u201d pomi\u0119dzy listami.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "To lista wybranych %s. Aby usun\u0105\u0107, zaznacz pozycje wybrane do usuni\u0119cia i kliknij strza\u0142k\u0119 \u201eUsu\u0144\u201d pomi\u0119dzy listami.",
    "This tag name cannot contain non-alphanumeric characters!": "Nazwa tego tagu mo\u017ce zawiera\u0107 jedynie znaki alfanumeryczne",
    "This tag name cannot have more than 30 characters!": "Nazwa tego tagu nie mo\u017ce przekroczy\u0107 30 znak\u00f3w!",
    "Today": "Dzisiaj",
    "Tomorrow": "Jutro",
    "Try selecting your company from the type-ahead results.": "Spr\u00f3buj wybra\u0107 swoj\u0105 firm\u0119 spo\u015br\u00f3d pojawiaj\u0105cych si\u0119 podpowiedzi",
    "Type into this box to filter down the list of available %s.": "Wpisz co\u015b tutaj, aby wyfiltrowa\u0107 list\u0119 dost\u0119pnych %s.",
    "Unenroll": "Wyrejestruj",
    "Unenroll Participants": "Wyrejestruj uczestnik\u00f3w",
    "Unenroll all selected participants from this course?": "Na pewno wyrejestrowa\u0107 wszystkich wybranych uczestnik\u00f3w z tego kursu?",
    "Updated user data!": "Zaktualizowano dane u\u017cytkownika",
    "Urban Airship URL": "Adres URL dla Urban Airship",
    "User successfully enrolled in course": "Uda\u0142o si\u0119 zarejestrowa\u0107 u\u017cytkownika na kurs",
    "User will be enrolled in course selected below.": "U\u017cytkownik zostanie zarejestrowany na kursy wybrane poni\u017cej.",
    "Username": "Nazwa u\u017cytkownika",
    "Username can't be empty! ": "Nazwa u\u017cytkownika nie mo\u017ce by\u0107 pusta!",
    "View Details": "Zobacz szczeg\u00f3\u0142y",
    "We'll e-mail you when your report is ready to download.": "Wy\u015blemy Ci e-mail, gdy raport b\u0119dzie gotowy do pobrania.",
    "Webinar": "Webinarium",
    "Welcome to McKinsey Academy": "Witamy w McKinsey Academy",
    "What would you like to do now?": "Co chcia\u0142by\u015b teraz zrobi\u0107?",
    "Yesterday": "Wczoraj",
    "You are about to delete email template. Are you sure?": "To dzia\u0142anie spowoduje usuni\u0119cie szablonu e-mail. Czy chcesz kontynuowa\u0107?",
    "You can only add up to 4 fields": "Mo\u017cesz doda\u0107 tylko do 4 p\u00f3l",
    "You don't have permission to create a new tag, please select one from the list!": "Nie posiadasz uprawnie\u0144 pozwalaj\u0105cych na stworzenie nowego tagu, prosimy wybra\u0107 tag z listy",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Wybrano akcj\u0119, lecz nie dokonano \u017cadnych zmian w polach. Prawdopodobnie szukasz przycisku \u201eWykonaj\u201d, a nie \u201eZapisz\u201d.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Wybrano akcj\u0119, lecz cz\u0119\u015b\u0107 zmian w polach nie zosta\u0142a zachowana. Kliknij OK, aby zapisa\u0107. Aby wykona\u0107 akcj\u0119, nale\u017cy j\u0105 ponownie uruchomi\u0107.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Zmiany w niekt\u00f3rych polach nie zosta\u0142y zachowane. Po wykonaniu akcji, zmiany te zostan\u0105 utracone.",
    "You need to enter course ID!": "Musisz wprowadzi\u0107 numer identyfikacyjny kursu!",
    "You need to enter name!": "Musisz wprowadzi\u0107 imi\u0119!",
    "You need to select at least one participant to be able to apply bulk actions.": "Musisz wybra\u0107 przynajmniej jednego uczestnika, aby zastosowa\u0107 akcje masowe.",
    "You need to select course!": "Musisz wybra\u0107 kurs!",
    "You need to select status!": "Musisz wybra\u0107 status!",
    "You were logged out due to inactivity. Please log back in to continue.": "Zosta\u0142e\u015b wylogowany z powodu zbyt d\u0142ugiej nieaktywno\u015bci. Aby kontynuowa\u0107, zaloguj si\u0119 ponownie.",
    "Your Progress: %(value)s%": "Tw\u00f3j stopie\u0144 uko\u0144czenia: %(value)s%",
    "Your course begins in %(days)s day.": [
      "Tw\u00f3j kurs rozpocznie si\u0119 za %(days)s dzie\u0144.",
      "Tw\u00f3j kurs rozpocznie si\u0119 za %(days)s dni."
    ],
    "Your course hasn't begun yet. ": "Tw\u00f3j kurs jeszcze si\u0119 nie rozpocz\u0105\u0142.",
    "complete": "uko\u0144czono",
    "contains %s learner": [
      "zawiera %s ucznia.",
      "zawiera %s uczni\u00f3w."
    ],
    "course id": "numer identyfikacyjny kursu",
    "course_id": "course_id",
    "email": "e-mail",
    "iOS DL URL": "iOS DL URL",
    "location": "lokalizacja",
    "one letter Friday\u0004F": "P",
    "one letter Monday\u0004M": "P",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "N",
    "one letter Thursday\u0004T": "C",
    "one letter Tuesday\u0004T": "W",
    "one letter Wednesday\u0004W": "\u015a",
    "participant_id": "participant_id",
    "same as your organization's average": "tak samo, jak \u015brednia Twojej organizacji",
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
    "DATETIME_FORMAT": "j E Y H:i",
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
    "DATE_FORMAT": "j E Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%y-%m-%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j E",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d-m-Y  H:i",
    "SHORT_DATE_FORMAT": "d-m-Y",
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

