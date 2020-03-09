

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
    " day": "d\u00eda",
    " week": "semana",
    "# of people": "Cantidad de personas",
    "% total cohort": "% del grupo total",
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s curso etiquetado con %(tagDetails)s",
      "%(count)s cursos etiquetados con %(tagDetails)s",
      "",
      "",
      "",
      ""
    ],
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s Antes de ello, puede explorar el sitio para obtener m\u00e1s informaci\u00f3n sobre qu\u00e9 esperar del curso.",
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s de %(cnt)s seleccionado",
      "%(sel)s de  %(cnt)s seleccionados",
      "",
      "",
      "",
      ""
    ],
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "%(selectedRows)s participantes se inscribir\u00e1n en el curso seleccionado a continuaci\u00f3n.",
      "%(selectedRows)s participante se inscribir\u00e1 en el curso seleccionado a continuaci\u00f3n.",
      "",
      "",
      "",
      ""
    ],
    "%(value)s%": "%(value)s%",
    "%s invalid email was ignored.": [
      "%s correo electr\u00f3nico no v\u00e1lido se omiti\u00f3.",
      "%s correos electr\u00f3nicos no v\u00e1lidos se omitieron.",
      "%s correos electr\u00f3nicos no v\u00e1lidos se omitieron.",
      "%s correos electr\u00f3nicos no v\u00e1lidos se omitieron.",
      "%s correos electr\u00f3nicos no v\u00e1lidos se omitieron.",
      "%s correos electr\u00f3nicos no v\u00e1lidos se omitieron."
    ],
    "%s learner has been added to this cohort.": [
      "%s participante se ha agregado a este grupo.",
      "%s participantes se han agregado a este grupo.",
      "%s participantes se han agregado a este grupo.",
      "%s participantes se han agregado a este grupo.",
      "%s participantes se han agregado a este grupo.",
      "%s participantes se han agregado a este grupo."
    ],
    "%s learner has been moved to this cohort.": [
      "%s participante se ha cambiado a este grupo.",
      "%s participantes se han cambiado a este grupo.",
      "%s participantes se han cambiado a este grupo.",
      "%s participantes se han cambiado a este grupo.",
      "%s participantes se han cambiado a este grupo.",
      "%s participantes se han cambiado a este grupo."
    ],
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "%s participante se asign\u00f3 previamente a este grupo. Este participante se agregar\u00e1 autom\u00e1ticamente al grupo cuando se inscriba en el curso.",
      "%s participantes se asignaron previamente a este grupo. Estos participantes se agregar\u00e1n autom\u00e1ticamente al grupo cuando se inscriban en el curso.",
      "%s participantes se asignaron previamente a este grupo. Estos participantes se agregar\u00e1n autom\u00e1ticamente al grupo cuando se inscriban en el curso.",
      "%s participantes se asignaron previamente a este grupo. Estos participantes se agregar\u00e1n autom\u00e1ticamente al grupo cuando se inscriban en el curso.",
      "%s participantes se asignaron previamente a este grupo. Estos participantes se agregar\u00e1n autom\u00e1ticamente al grupo cuando se inscriban en el curso.",
      "%s participantes se asignaron previamente a este grupo. Estos participantes se agregar\u00e1n autom\u00e1ticamente al grupo cuando se inscriban en el curso."
    ],
    "%s user was already in this cohort.": [
      "%s usuario ya estaba en este grupo.",
      "%s usuarios ya estaban en este grupo.",
      "%s usuarios ya estaban en este grupo.",
      "%s usuarios ya estaban en este grupo.",
      "%s usuarios ya estaban en este grupo.",
      "%s usuarios ya estaban en este grupo."
    ],
    "%s user/email was not found.": [
      "%s nombre de usuario o correo electr\u00f3nico no se encontr\u00f3.",
      "%s nombres de usuario o correos electr\u00f3nicos no se encontraron.",
      "%s nombres de usuario o correos electr\u00f3nicos no se encontraron.",
      "%s nombres de usuario o correos electr\u00f3nicos no se encontraron.",
      "%s nombres de usuario o correos electr\u00f3nicos no se encontraron.",
      "%s nombres de usuario o correos electr\u00f3nicos no se encontraron."
    ],
    ".0%": ".0%",
    "2 or more fields can not have the same name": "Dos o m\u00e1s campos no pueden tener el mismo nombre",
    "6 a.m.": "6 a.m.",
    "6 p.m.": "6 p.m.",
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "<span class=\"green\"> %(diff)s punto</span> superior al promedio de su organizaci\u00f3n",
      "<span class=\"green\"> %(diff)s puntos</span> superior al promedio de su organizaci\u00f3n",
      "<span class=\"green\"> %(diff)s puntos</span> superior al promedio de su organizaci\u00f3n",
      "<span class=\"green\"> %(diff)s puntos</span> superior al promedio de su organizaci\u00f3n",
      "<span class=\"green\"> %(diff)s puntos</span> superior al promedio de su organizaci\u00f3n",
      "<span class=\"green\"> %(diff)s puntos</span> superior al promedio de su organizaci\u00f3n"
    ],
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "<span class=\"green\">%(diff)s% </span> superior al promedio de su organizaci\u00f3n",
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "<span class=\"red\"> %(diff)s punto</span> inferior al promedio de su organizaci\u00f3n",
      "<span class=\"red\"> %(diff)s puntos</span> inferior al promedio de su organizaci\u00f3n",
      "<span class=\"red\"> %(diff)s puntos</span> inferior al promedio de su organizaci\u00f3n",
      "<span class=\"red\"> %(diff)s puntos</span> inferior al promedio de su organizaci\u00f3n",
      "<span class=\"red\"> %(diff)s puntos</span> inferior al promedio de su organizaci\u00f3n",
      "<span class=\"red\"> %(diff)s puntos</span> inferior al promedio de su organizaci\u00f3n"
    ],
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "<span class=\"red\"> %(diff)s% </span> inferior al promedio de su organizaci\u00f3n",
    "Activated": "Activado",
    "Activation File": "Enlace de activaci\u00f3n",
    "Activation Link": "Enlace de activaci\u00f3n",
    "Active": "Activo",
    "Add new role e.g CEO,CTO": "Agregue un rol nuevo, por ejemplo, CEO, CTO",
    "Admin Company": "Compa\u00f1\u00eda administradora",
    "Admin Permissions": "Permisos de administrador",
    "All students added to private group have to be members of same company.": "Todos los alumnos agregados al grupo privado deben ser miembros de la misma compa\u00f1\u00eda.",
    "An error occurred submitting the request.": "Hubo un error al enviar la solicitud.",
    "Analytics URL": "URL de anal\u00edtica",
    "Android DL URL": "URL de Android DL",
    "Announcements": "Anuncios",
    "App Name": "Nombre de la aplicaci\u00f3n",
    "April": "Abril",
    "Are you sure you want to remove this ?": "\u00bfEst\u00e1 seguro de que desea eliminar esto?",
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "\u00bfEst\u00e1 seguro de que desea eliminar este grupo? Si lo hace, se eliminar\u00e1n las entregas y el feedback asociados al grupo.",
    "Are you sure?": "\u00bfEst\u00e1 seguro?",
    "Assessment: %(label)s": "Evaluaci\u00f3n: %(label)s",
    "August": "Agosto",
    "Available %s": "%s Disponibles",
    "Avg Progress": "Avance promedio",
    "Business Function": "Funci\u00f3n de negocio",
    "Business Unit": "Unidad de negocio",
    "Cancel": "Cancelar",
    "Change Status": "Cambiar estado",
    "Change status of all selected participants to:": "Cambiar el estado de todos los participantes seleccionados a:",
    "Check for Completion": "Verifique que est\u00e9 completo.",
    "Choose": "Elegir",
    "Choose a Date": "Elija una fecha",
    "Choose a Time": "Elija una hora",
    "Choose a time": "Elija una hora",
    "Choose all": "Selecciona todos",
    "Chosen %s": "%s elegidos",
    "Click Add to specify Lesson Label": "Haga clic en Agregar para especificar la Etiqueta de la lecci\u00f3n",
    "Click Add to specify Lessons Label": "Haga clic en Agregar para especificar la Etiqueta de las lecciones",
    "Click Add to specify Module Label": "Haga clic en Agregar para especificar la Etiqueta del m\u00f3dulo",
    "Click Add to specify Modules Label": "Haga clic en Agregar para especificar la Etiqueta de los m\u00f3dulos",
    "Click to choose all %s at once.": "Haga clic para seleccionar todos los %s de una vez",
    "Click to remove all chosen %s at once.": "Haz clic para eliminar todos los %s elegidos",
    "Cohort": "Composici\u00f3n del grupo",
    "Cohort Comp.": "Composici\u00f3n del grupo",
    "Company": "Compa\u00f1\u00eda",
    "Company Admin": "Administrador de la compa\u00f1\u00eda",
    "Company ID": "ID de la compa\u00f1\u00eda",
    "Company doesn't exist! ": "La compa\u00f1\u00eda no existe",
    "Complete": "Completado",
    "Complete all content to continue": "Complete todo el contenido para continuar.",
    "Complete all content to continue.": "Complete todo el contenido para continuar.",
    "Completed": "Completado",
    "Contains Errors": "Mostrar errores",
    "Content is complete, please continue.": "El contenido est\u00e1 completo. Puede continuar.",
    "Couldn't add tag to course!": "No se pudo agregar la etiqueta al curso",
    "Couldn't create new company!": "No se pudo crear la nueva compa\u00f1\u00eda",
    "Couldn't create new tag!": "No se pudo crear la nueva etiqueta",
    "Couldn't delete tag!": "No se pudo eliminar la etiqueta",
    "Couldn't delink App!": "No se pudo desvincular la aplicaci\u00f3n",
    "Couldn't link this App!": "No se pudo vincular la aplicaci\u00f3n",
    "Country": "Pa\u00eds",
    "Course": "Curso",
    "Course ID": "ID del curso",
    "Course Name": "Nombre del curso",
    "Dashboard Name": "Nombre del panel",
    "Date Added": "Se agreg\u00f3 la fecha",
    "December": "Diciembre",
    "Delete Role": "Eliminar rol",
    "Deployment Mech": "Mecanismo de despliegue",
    "Digital Content": "Contenido digital",
    "Digital Course": "Curso digital",
    "Discussion": "Debates",
    "Do you really want to delete: \n": "\u00bfRealmente desea eliminar esto?: \n",
    "Download": "Descargar",
    "Download CSV File": "Descargar archivo CSV",
    "Download Notifications CSV": "Descargar CSV para notificaciones",
    "Email": "Correo electr\u00f3nico",
    "Email Preview Success!": "Vista previa de correo electr\u00f3nico generada exitosamente",
    "Email Success!": "Correo electr\u00f3nico generado exitosamente",
    "Email can't be empty! ": "El correo electr\u00f3nico no puede quedar vac\u00edo",
    "End": "Fin",
    "End Date": "Fecha de finalizaci\u00f3n",
    "End time": "Fecha de finalizaci\u00f3n",
    "Engagement": "Participaci\u00f3n en el curso",
    "Enroll Participant": "Inscribir participante",
    "Enroll Participants": "Inscribir participantes",
    "Enroll this list in another course": "Inscribir esta lista en otro curso",
    "Enrolled In": "Inscrito",
    "Error File": "Archivo de errores",
    "Error Occured!": "Hubo un error.",
    "Error initiating the report generation. Please retry later.": "No se pudo ejecutar la tarea. Vuelva a intentarlo m\u00e1s tarde.",
    "Error processing CSV file.": "Error al procesar el archivo CSV.",
    "Error uploading file. Please try again and be sure to use an accepted file format.": "Error al cargar el archivo. Int\u00e9ntelo de nuevo y aseg\u00farese de usar un formato de archivo aceptado.",
    "Export Report": "Exportar informe",
    "Exporting Stats for All Users": "Exportar estad\u00edsticas para todos los usuarios",
    "February": "Febrero",
    "Female": "Femenino",
    "Fetching data for file: %(filename)s": "Buscando datos del archivo: %(filename)s",
    "File name": "Nombre del archivo",
    "File successfully uploaded!": "El archivo se carg\u00f3 correctamente",
    "Filename": "Nombre de archivo",
    "Filter": "Filtro",
    "First name can't be empty! ": "El nombre no puede quedar vac\u00edo",
    "Go to %(course_id)s Course": "Ir al curso %(course_id)s",
    "Grade": "Calificaci\u00f3n",
    "Group Work": "Trabajo en grupo",
    "Group Work: %(label)s": "Trabajo en grupo: %(label)s",
    "Group successfully updated": "El grupo se actualiz\u00f3 correctamente",
    "Group was not created": "El grupo no se ha creado",
    "Group work": "Trabajo en grupo",
    "Hide": "Esconder",
    "Hide Details": "Ocultar detalles",
    "Hide password": "Ocultar contrase\u00f1a",
    "I'm Done": "Listo",
    "Importing %(processed)s of %(total)s rows": "Importando %(processed)s de %(total)s filas",
    "Importing..": "Importando...",
    "In Person Session": "Sesi\u00f3n presencial",
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "Incluir el desglose del proceso para cada sesi\u00f3n (nota: exportar tomar\u00e1 m\u00e1s tiempo)",
    "Incomplete": "Incompleto",
    "Initiated by": "Iniciado por",
    "Invalid format for CSV file.": "Formato no v\u00e1lido para el archivo CSV.",
    "It looks like you're not active. Click OK to keep working.": "Parece que no se encuentra activo. Haga clic en OK para seguir trabajando.",
    "It looks like your browser settings has pop-ups disabled.": "Parece que la configuraci\u00f3n de su buscador tiene desactivadas las ventanas emergentes.",
    "January": "Enero",
    "July": "Julio",
    "June": "Junio",
    "Last Log In": "\u00daltimo inicio de sesi\u00f3n",
    "Last name can't be empty! ": "El apellido no puede quedar vac\u00edo ",
    "Launch pop-up to continue": "Despliegue la ventana emergente para continuar.",
    "Leaderboards": "Tableros de calificaciones",
    "Learner email": "Correo electr\u00f3nico del participante",
    "Lesson": "Lecci\u00f3n",
    "Male": "Masculino",
    "Manager email": "Correo electr\u00f3nico del gerente",
    "March": "Marzo",
    "May": "Mayo",
    "Midnight": "Medianoche",
    "Moderator": "Moderador",
    "Module": "M\u00f3dulo",
    "Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.": "Debe tener al menos 8 caracteres e incluir letras may\u00fasculas y min\u00fasculas, adem\u00e1s de n\u00fameros O caracteres especiales.",
    "Name": "Nombre",
    "No App Display Name!": "No hay nombre de aplicaci\u00f3n para mostrar",
    "No Company Display Name!": "No hay nombre de la compa\u00f1\u00eda para mostrar",
    "No file Selected": "Ning\u00fan archivo seleccionado",
    "No. of Courses": "Cantidad de cursos",
    "No. of Participants": "Cantidad de participantes",
    "NoName": "Sin nombre",
    "None": "Ninguno",
    "Noon": "Mediod\u00eda",
    "Note: You are %s hour ahead of server time.": [
      "Nota: Usted esta a %s horas por delante de la hora del servidor.",
      "Nota: Usted va %s horas por delante de la hora del servidor.",
      "",
      "",
      "",
      ""
    ],
    "Note: You are %s hour behind server time.": [
      "Nota: Usted esta a %s hora de retraso de tiempo de servidor.",
      "Nota: Usted va %s horas por detr\u00e1s de la hora del servidor.",
      "",
      "",
      "",
      ""
    ],
    "Notification": "Notificaci\u00f3n",
    "November": "Noviembre",
    "Now": "Ahora",
    "Observer": "Observador",
    "October": "Octubre",
    "Only alphanumeric characters and spaces allowed": "Solo se permiten caracteres alfanum\u00e9ricos y espacios",
    "Participant": "Participante",
    "Participants": "Participantes",
    "Please enter new template name!": "Ingrese el nombre de la nueva plantilla",
    "Please enter preview email!": "Ingrese la vista previa de correo electr\u00f3nico",
    "Please enter updated template name or leave the old one!": "Ingrese el nombre actualizado de la plantilla o conserve el anterior",
    "Please select at least one course": "Seleccione al menos un curso",
    "Please select at least one student": "Seleccione al menos un alumno",
    "Please select file first.": "Seleccione el archivo primero.",
    "Please select file for upload.": "Seleccione un archivo para cargar.",
    "Please select project": "Seleccione el proyecto",
    "Poll/Survey Question": "Pregunta de encuesta o sondeo",
    "Preview Email!": "Vista previa de correo electr\u00f3nico",
    "Proficiency": "Competencia",
    "Program": "Programa",
    "Progress": "Avance",
    "Progress : 0%": "Progreso: 0 %",
    "Progress: %(progress)s %": "Avance: %(progress)s %",
    "Progress: %(value)s%": "Avance: %(value)s%",
    "Remove": "Eliminar",
    "Remove all": "Eliminar todos",
    "Report of bulk update will be sent to your email.": "El informe de la actualizaci\u00f3n general se enviar\u00e1 a su correo electr\u00f3nico.",
    "Request Time": "Tiempo de solicitud",
    "Save Changes": "Guardar cambios",
    "Search by Keyword": "Buscar por palabra clave",
    "Select Course": "Seleccionar curso",
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "Seleccionados: %(selected)s; exitosos: %(successful)s; fallidos: %(failed)s",
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "Seleccionados: %(selectedRows)s; exitosos: 0; fallidos: 0",
    "Send": "Enviar",
    "Send Course Intro Email": "Enviar correo electr\u00f3nico de introducci\u00f3n al curso",
    "September": "Septiembre",
    "Show": "Mostrar",
    "Show Errors": "Mostrar errores",
    "Show password": "Mostrar contrase\u00f1a",
    "Start": "Inicio",
    "Start time": "Inicio",
    "Status": "Estado",
    "Successful": "Exitoso",
    "Successfully Enrolled in 1 Course": "Correctamente inscrito en 1 curso",
    "Successfully added new template!": "La nueva plantilla se agreg\u00f3 correctamente",
    "Successfully deleted template!": "La plantilla se elimin\u00f3 correctamente",
    "Successfully sent email!": "El correo electr\u00f3nico se envi\u00f3 exitosamente",
    "Successfully sent preview email!": "La vista previa de correo electr\u00f3nico se envi\u00f3 exitosamente",
    "Successfully updated template!": "La plantilla se actualiz\u00f3 correctamente",
    "TA": "TA",
    "Task failed to execute. Please retry later.": "No se pudo ejecutar la tarea. Vuelva a intentarlo m\u00e1s tarde.",
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "El archivo .csv tiene m\u00e1s de %(limit)s filas: %(lines)s ; div\u00eddalo en m\u00e1s archivos",
    "The content takes place in a new window.": "El contenido se despliega en una ventana nueva.",
    "There was an error submitting your file.": "Hubo un error al enviar el archivo.",
    "This app name cannot contain non-alphanumeric characters!": "El nombre de aplicaci\u00f3n solo puede contener caracteres alfanum\u00e9ricos",
    "This app name cannot have more than 30 characters!": "El nombre de aplicaci\u00f3n no puede tener m\u00e1s de 30 caracteres",
    "This company name cannot contain non-alphanumeric characters!": "El nombre de compa\u00f1\u00eda solo puede contener caracteres alfanum\u00e9ricos",
    "This company name cannot have more than 30 characters!": "El nombre de compa\u00f1\u00eda no puede tener m\u00e1s de 30 caracteres",
    "This field is required.": "Este campo es obligatorio.",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Esta es la lista de %s disponibles. Puede elegir algunos seleccion\u00e1ndolos en la caja inferior y luego haciendo clic en la flecha \"Elegir\" que hay entre las dos cajas.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Esta es la lista de los %s elegidos. Puede elmininar algunos seleccion\u00e1ndolos en la caja inferior y luego haciendo click en la flecha \"Eliminar\" que hay entre las dos cajas.",
    "This tag name cannot contain non-alphanumeric characters!": "El nombre de etiqueta solo puede contener caracteres alfanum\u00e9ricos",
    "This tag name cannot have more than 30 characters!": "El nombre de etiqueta no puede tener m\u00e1s de 30 caracteres",
    "Today": "Hoy",
    "Today at ": "hoy",
    "Tomorrow": "Ma\u00f1ana",
    "Try selecting your company from the type-ahead results.": "Intente seleccionar su compa\u00f1\u00eda en los resultados de escritura autom\u00e1tica.",
    "Type into this box to filter down the list of available %s.": "Escriba en este cuadro para filtrar la lista de %s disponibles",
    "Unenroll": "Cancelar inscripci\u00f3n",
    "Unenroll Participants": "Cancelar inscripci\u00f3n de participantes",
    "Unenroll all selected participants from this course?": "\u00bfDesea cancelar la inscripci\u00f3n de todos los participantes seleccionados en este curso?",
    "Updated user data!": "Se actualizaron los datos del usuario",
    "Urban Airship URL": "URL de Urban Airship",
    "User successfully enrolled in course": "Se inscribi\u00f3 correctamente al usuario en el curso",
    "User will be enrolled in course selected below.": "Se inscribir\u00e1 al usuario en el curso seleccionado a continuaci\u00f3n.",
    "Username": "Nombre de usuario",
    "Username can't be empty! ": "El nombre de usuario no puede quedar vac\u00edo",
    "View Details": "Ver detalles",
    "We'll e-mail you when your report is ready to download.": "Le enviaremos un correo electr\u00f3nico cuando el informe est\u00e9 listo para descargarlo.",
    "Webinar": "Seminario web",
    "Welcome to McKinsey Academy": "Bienvenido a McKinsey Academy",
    "What would you like to do now?": "\u00bfQu\u00e9 desea hacer ahora?",
    "Yesterday": "Ayer",
    "You are about to delete email template. Are you sure?": "Est\u00e1 a punto de eliminar la plantilla de correo electr\u00f3nico. \u00bfEst\u00e1 seguro?",
    "You are now": "tu eres ahora",
    "You can only add up to 4 fields": "Puede agregar un m\u00e1ximo de cuatro (4) campos",
    "You don't have permission to create a new tag, please select one from the list!": "No tiene permiso para crear una nueva etiqueta. Seleccione una de la lista",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Ha seleccionado una acci\u00f3n y no hs hecho ning\u00fan cambio en campos individuales. Probablemente est\u00e9 buscando el bot\u00f3n Ejecutar en lugar del bot\u00f3n Guardar.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Ha seleccionado una acci\u00f3n, pero no ha guardado los cambios en los campos individuales todav\u00eda. Pulse OK para guardar. Tendr\u00e1 que volver a ejecutar la acci\u00f3n.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Tiene cambios sin guardar en campos editables individuales. Si ejecuta una acci\u00f3n, los cambios no guardados se perder\u00e1n.",
    "You need to enter course ID!": "Debe ingresar el ID del curso",
    "You need to enter name!": "Debe ingresar el nombre",
    "You need to select at least one participant to be able to apply bulk actions.": "Debe seleccionar al menos un participante para poder aplicar acciones en forma masiva",
    "You need to select course!": "Debe seleccionar un curso",
    "You need to select status!": "Debe seleccionar un estado",
    "You were logged out due to inactivity. Please log back in to continue.": "Su sesi\u00f3n expir\u00f3 por estar inactiva. Inicie sesi\u00f3n de nuevo para continuar.",
    "Your Progress: %(value)s%": "Su avance: %(value)s%",
    "Your course begins in %(days)s day.": [
      "Su curso comienza en %(days)s d\u00eda.",
      "Su curso comienza en %(days)s d\u00edas.",
      "Su curso comienza en %(days)s d\u00edas.",
      "Su curso comienza en %(days)s d\u00edas.",
      "Su curso comienza en %(days)s d\u00edas.",
      "Su curso comienza en %(days)s d\u00edas."
    ],
    "Your course hasn't begun yet. ": "Su curso a\u00fan no ha comenzado. ",
    "complete": "Incompleto",
    "contains %s learner": [
      "contiene %s participante",
      "contiene %s participantes",
      "contiene %s participantes",
      "contiene %s participantes",
      "contiene %s participantes",
      "contiene %s participantes"
    ],
    "course id": "ID del curso",
    "email": "correo electr\u00f3nico",
    "for": "en",
    "iOS DL URL": "URL de iOS DL",
    "in the cohort!": "en el grupo.",
    "location": "Notificaci\u00f3n",
    "one letter Friday\u0004F": "V",
    "one letter Monday\u0004M": "L",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "J",
    "one letter Tuesday\u0004T": "M",
    "one letter Wednesday\u0004W": "M",
    "same as your organization's average": "igual al promedio de su organizaci\u00f3n",
    "status": "estado"
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
    "DATETIME_FORMAT": "j \\d\\e F \\d\\e Y \\a \\l\\a\\s H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%y %H:%M:%S",
      "%d/%m/%y %H:%M:%S.%f",
      "%d/%m/%y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j \\d\\e F \\d\\e Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j \\d\\e F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d/m/Y H:i",
    "SHORT_DATE_FORMAT": "d/m/Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F \\d\\e Y"
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

