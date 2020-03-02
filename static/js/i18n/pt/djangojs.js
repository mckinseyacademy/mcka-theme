

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
    " day": " dia",
    " week": " semana",
    "# of people": "N\u00ba de pessoas",
    "% total cohort": "% do grupo total",
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s curso marcado com %(tagDetails)s",
      "%(count)s cursos marcados com %(tagDetails)s",
      "",
      "",
      "",
      ""
    ],
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s Antes do in\u00edcio do curso, voc\u00ea pode explorar o site para saber mais sobre o que esperar.",
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s de %(cnt)s selecionado",
      "%(sel)s de %(cnt)s selecionados",
      "",
      "",
      "",
      ""
    ],
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "Os participantes %(selectedRows)s ser\u00e3o inscritos no curso selecionado abaixo.",
      "O participante %(selectedRows)s ser\u00e1 inscrito no curso selecionado abaixo.",
      "",
      "",
      "",
      ""
    ],
    "%(value)s%": "%(value)s%",
    "%s invalid email was ignored.": [
      "O e-mail inv\u00e1lido %s foi ignorado.",
      "Os e-mails inv\u00e1lidos %s foram ignorados.",
      "Os e-mails inv\u00e1lidos %s foram ignorados.",
      "Os e-mails inv\u00e1lidos %s foram ignorados.",
      "Os e-mails inv\u00e1lidos %s foram ignorados.",
      "Os e-mails inv\u00e1lidos %s foram ignorados."
    ],
    "%s learner has been added to this cohort.": [
      "O aluno %s foi adicionado a este grupo.",
      "Os alunos %s foram adicionados a este grupo.",
      "Os alunos %s foram adicionados a este grupo.",
      "Os alunos %s foram adicionados a este grupo.",
      "Os alunos %s foram adicionados a este grupo.",
      "Os alunos %s foram adicionados a este grupo."
    ],
    "%s learner has been moved to this cohort.": [
      "O aluno %s foi movido para este grupo.",
      "Os alunos %s foram movidos para este grupo.",
      "Os alunos %s foram movidos para este grupo.",
      "Os alunos %s foram movidos para este grupo.",
      "Os alunos %s foram movidos para este grupo.",
      "Os alunos %s foram movidos para este grupo."
    ],
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "O aluno %s foi pr\u00e9-atribu\u00eddo a este grupo. Esse aluno ser\u00e1 automaticamente adicionado ao grupo quando se inscrever no curso.",
      "Os alunos %s foram pr\u00e9-atribu\u00eddos a este grupo. Esses alunos ser\u00e3o automaticamente adicionados ao grupo quando se inscreverem no curso.",
      "Os alunos %s foram pr\u00e9-atribu\u00eddos a este grupo. Esses alunos ser\u00e3o automaticamente adicionados ao grupo quando se inscreverem no curso.",
      "Os alunos %s foram pr\u00e9-atribu\u00eddos a este grupo. Esses alunos ser\u00e3o automaticamente adicionados ao grupo quando se inscreverem no curso.",
      "Os alunos %s foram pr\u00e9-atribu\u00eddos a este grupo. Esses alunos ser\u00e3o automaticamente adicionados ao grupo quando se inscreverem no curso.",
      "Os alunos %s foram pr\u00e9-atribu\u00eddos a este grupo. Esses alunos ser\u00e3o automaticamente adicionados ao grupo quando se inscreverem no curso."
    ],
    "%s user was already in this cohort.": [
      "O usu\u00e1rio %s j\u00e1 est\u00e1 neste grupo.",
      "Os usu\u00e1rios %s j\u00e1 est\u00e3o neste grupo.",
      "Os usu\u00e1rios %s j\u00e1 est\u00e3o neste grupo.",
      "Os usu\u00e1rios %s j\u00e1 est\u00e3o neste grupo.",
      "Os usu\u00e1rios %s j\u00e1 est\u00e3o neste grupo.",
      "Os usu\u00e1rios %s j\u00e1 est\u00e3o neste grupo."
    ],
    "%s user/email was not found.": [
      "O usu\u00e1rio/e-mail %s n\u00e3o foi encontrado.",
      "Os usu\u00e1rios/e-mail %s n\u00e3o foram encontrados.",
      "Os usu\u00e1rios/e-mail %s n\u00e3o foram encontrados.",
      "Os usu\u00e1rios/e-mail %s n\u00e3o foram encontrados.",
      "Os usu\u00e1rios/e-mail %s n\u00e3o foram encontrados.",
      "Os usu\u00e1rios/e-mail %s n\u00e3o foram encontrados."
    ],
    ".0%": ".0%",
    "2 or more fields can not have the same name": "2 ou mais campos n\u00e3o podem ter o mesmo nome",
    "6 a.m.": "6 a.m.",
    "6 p.m.": "6 p.m.",
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "<span class=\"green\"> %(diff)s ponto</span> acima da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"green\"> %(diff)s pontos</span> acima da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"green\"> %(diff)s pontos</span> acima da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"green\"> %(diff)s pontos</span> acima da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"green\"> %(diff)s pontos</span> acima da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"green\"> %(diff)s pontos</span> acima da m\u00e9dia da sua organiza\u00e7\u00e3o"
    ],
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "<span class=\"green\">%(diff)s% </span> acima da m\u00e9dia da sua organiza\u00e7\u00e3o",
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "<span class=\"red\"> %(diff)s ponto</span> abaixo da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"red\"> %(diff)s pontos</span> abaixo da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"red\"> %(diff)s pontos</span> abaixo da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"red\"> %(diff)s pontos</span> abaixo da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"red\"> %(diff)s pontos</span> abaixo da m\u00e9dia da sua organiza\u00e7\u00e3o",
      "<span class=\"red\"> %(diff)s pontos</span> abaixo da m\u00e9dia da sua organiza\u00e7\u00e3o"
    ],
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "<span class=\"red\"> %(diff)s% </span> abaixo da m\u00e9dia da sua organiza\u00e7\u00e3o",
    "Activated": "Ativado",
    "Activation File": "Arquivo de ativa\u00e7\u00e3o",
    "Activation Link": "Link de ativa\u00e7\u00e3o",
    "Active": "Ativo",
    "Add new role e.g CEO,CTO": "Adicionar nova fun\u00e7\u00e3o, por exemplo, CEO, CTO",
    "Admin Company": "Empresa do administrador",
    "Admin Permissions": "Permiss\u00f5es do administrador",
    "All students added to private group have to be members of same company.": "Todos os alunos adicionados ao grupo privado devem ser membros da mesma empresa.",
    "An error occurred submitting the request.": "Ocorreu um erro ao enviar a solicita\u00e7\u00e3o.",
    "Analytics URL": "URL do Analytics",
    "Android DL URL": "URL do Android DL",
    "Announcements": "Avisos",
    "App Name": "Nome do aplicativo",
    "April": "Abril",
    "Are you sure you want to remove this ?": "Tem certeza que deseja remover?",
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "Tem certeza que deseja remover este grupo? Ao fazer isso, voc\u00ea remover\u00e1 os envios e coment\u00e1rios associados a ele.",
    "Are you sure?": "Tem certeza?",
    "Assessment: %(label)s": "Avalia\u00e7\u00e3o: %(label)s",
    "August": "Agosto",
    "Available %s": "Dispon\u00edvel %s",
    "Avg Progress": "Progresso m\u00e9dio",
    "Business Function": "Fun\u00e7\u00e3o comercial",
    "Business Unit": "Unidade de neg\u00f3cios",
    "Cancel": "Cancelar",
    "Change Status": "Alterar status",
    "Change status of all selected participants to:": "Alterar o status de todos os participantes selecionados para:",
    "Check for Completion": "Verifica\u00e7\u00e3o de Conclus\u00e3o",
    "Choose": "Escolher",
    "Choose a Date": "Escolha a Data",
    "Choose a Time": "Escolha a Hora",
    "Choose a time": "Escolha a hora",
    "Choose all": "Escolher todos",
    "Chosen %s": "Escolhido %s",
    "Click Add to specify Lesson Label": "Clique em Adicionar para especificar o r\u00f3tulo da li\u00e7\u00e3o",
    "Click Add to specify Lessons Label": "Clique em Adicionar para especificar o r\u00f3tulo das li\u00e7\u00f5es",
    "Click Add to specify Module Label": "Clique em Adicionar para especificar o r\u00f3tulo do m\u00f3dulo",
    "Click Add to specify Modules Label": "Clique em Adicionar para especificar o r\u00f3tulo dos m\u00f3dulos",
    "Click to choose all %s at once.": "Clique para escolher todos os %s de uma vez.",
    "Click to remove all chosen %s at once.": "Clique para remover todos os %s escolhidos de uma vez.",
    "Cohort": "Grupo",
    "Cohort Comp.": "Empresa do grupo",
    "Company": "Empresa",
    "Company Admin": "Administrador da empresa",
    "Company ID": "ID da empresa",
    "Company doesn't exist! ": "A empresa n\u00e3o existe!",
    "Complete": "Completo",
    "Complete all content to continue": "Complete todo o conte\u00fado para continuar",
    "Complete all content to continue.": "Complete todo o conte\u00fado para continuar",
    "Completed": "Conclu\u00eddo",
    "Contains Errors": "Cont\u00e9m erros",
    "Content is complete, please continue.": "O conte\u00fado est\u00e1 completo, por favor, continue",
    "Couldn't add tag to course!": "N\u00e3o foi poss\u00edvel adicionar tag ao curso!",
    "Couldn't create new company!": "N\u00e3o foi poss\u00edvel criar nova empresa!",
    "Couldn't create new tag!": "N\u00e3o foi poss\u00edvel criar uma nova tag!",
    "Couldn't delete tag!": "N\u00e3o foi poss\u00edvel excluir a tag!",
    "Couldn't delink App!": "N\u00e3o foi poss\u00edvel desvincular o aplicativo!",
    "Couldn't link this App!": "N\u00e3o foi poss\u00edvel vincular este aplicativo!",
    "Country": "Pa\u00eds",
    "Course": "Curso",
    "Course ID": "ID do curso",
    "Course Name": "Nome do curso",
    "Dashboard Name": "Nome do painel",
    "Date Added": "Data adicionada",
    "December": "Dezembro",
    "Delete Role": "Excluir fun\u00e7\u00e3o",
    "Deployment Mech": "Mecanismo de implanta\u00e7\u00e3o",
    "Digital Content": "Conte\u00fado digital",
    "Digital Course": "Curso digital",
    "Discussion": "Discuss\u00f5es",
    "Do you really want to delete: \n": "Voc\u00ea realmente deseja excluir:\n",
    "Download": "Download",
    "Download CSV File": "Baixar arquivo CSV",
    "Download Notifications CSV": "Download de notifica\u00e7\u00f5es em CSV",
    "Email": "E-mail",
    "Email Preview Success!": "Visualiza\u00e7\u00e3o de e-mail bem-sucedida!",
    "Email Success!": "E-mail bem-sucedido!",
    "Email can't be empty! ": "O e-mail n\u00e3o pode estar vazio!",
    "End": "Fim",
    "End Date": "Data de t\u00e9rmino",
    "End time": "Hora de t\u00e9rmino",
    "Engagement": "Engajamento",
    "Enroll Participant": "Inscrever participante",
    "Enroll Participants": "Inscrever participantes",
    "Enroll this list in another course": "Inscrever esta lista em outro curso",
    "Enrolled In": "Inscrito em",
    "Error File": "Arquivo de erro",
    "Error Occured!": "Ocorreu um erro!",
    "Error initiating the report generation. Please retry later.": "Erro ao iniciar a gera\u00e7\u00e3o do relat\u00f3rio. Tente novamente mais tarde.",
    "Error processing CSV file.": "Erro no processamento do arquivo CSV.",
    "Error uploading file. Please try again and be sure to use an accepted file format.": "Erro no upload do arquivo. Tente novamente e certifique-se de usar um formato de arquivo aceito.",
    "Export Report": "Exportar relat\u00f3rio",
    "Exporting Stats for All Users": "Exporta\u00e7\u00e3o de estat\u00edsticas para todos os usu\u00e1rios",
    "February": "Fevereiro",
    "Female": "Feminino",
    "Fetching data for file: %(filename)s": "Buscando dados para o arquivo: %(filename)s",
    "File name": "Nome do arquivo",
    "File successfully uploaded!": "Arquivo carregado com sucesso!",
    "Filename": "Nome do arquivo",
    "Filter": "Filtrar",
    "First name can't be empty! ": "O nome n\u00e3o pode estar vazio!",
    "Go to %(course_id)s Course": "V\u00e1 para o curso %(course_id)s",
    "Grade": "Nota",
    "Group Work": "Trabalho em equipe",
    "Group Work: %(label)s": "Grupo de trabalho: %(label)s",
    "Group successfully updated": "Grupo atualizado com sucesso",
    "Group was not created": "Grupo n\u00e3o criado",
    "Group work": "Trabalho em grupo",
    "Hide": "Ocultar",
    "Hide Details": "Ocultar detalhes",
    "Hide password": "Wachtwoord verbergen",
    "I'm Done": "Terminei",
    "Importing %(processed)s of %(total)s rows": "Importando %(processed)s de %(total)s linhas",
    "Importing..": "Importando...",
    "In Person Session": "Sess\u00e3o presencial",
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "Incluir detalhamento do progresso para cada li\u00e7\u00e3o (Observa\u00e7\u00e3o: a exporta\u00e7\u00e3o levar\u00e1 mais tempo)",
    "Incomplete": "Incompleto",
    "Initiated by": "Iniciado por",
    "Invalid format for CSV file.": "Formato inv\u00e1lido do arquivo CSV.",
    "It looks like you're not active. Click OK to keep working.": "Parece que voc\u00ea n\u00e3o est\u00e1 ativo. Clique em OK para continuar a trabalhar.",
    "It looks like your browser settings has pop-ups disabled.": "Aparentemente as configura\u00e7\u00f5es do seu navegador tem pop-ups desativados.",
    "January": "Janeiro",
    "July": "Julho",
    "June": "Junho",
    "Last Log In": "\u00daltimo login",
    "Last name can't be empty! ": "O sobrenome n\u00e3o pode estar vazio!",
    "Launch pop-up to continue": "Lan\u00e7ar pop-up para continuar",
    "Leaderboards": "Classifica\u00e7\u00f5es",
    "Learner email": "E-mail do aluno",
    "Lesson": "Li\u00e7\u00e3o",
    "Male": "Masculino",
    "Manager email": "E-mail do gerente",
    "March": "Mar\u00e7o",
    "May": "Maio",
    "Midnight": "Meia-noite",
    "Moderator": "Moderador",
    "Module": "M\u00f3dulo",
    "Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.": "Deve ter no m\u00ednimo 8 caracteres e incluir letras mai\u00fasculas e min\u00fasculas - al\u00e9m de n\u00fameros OU caracteres especiais.",
    "Name": "Nome",
    "No App Display Name!": "Nenhum nome de exibi\u00e7\u00e3o do aplicativo!",
    "No Company Display Name!": "Nenhum nome de exibi\u00e7\u00e3o da empresa!",
    "No file Selected": "Nenhum arquivo selecionado",
    "No. of Courses": "N\u00ba de cursos",
    "No. of Participants": "N\u00ba de participantes",
    "NoName": "SemNome",
    "None": "Nenhum",
    "Noon": "Meio-dia",
    "Note: You are %s hour ahead of server time.": [
      "Nota: O seu fuso hor\u00e1rio est\u00e1 %s hora adiantado em rela\u00e7\u00e3o ao servidor.",
      "Nota: O seu fuso hor\u00e1rio est\u00e1 %s horas adiantado em rela\u00e7\u00e3o ao servidor.",
      "",
      "",
      "",
      ""
    ],
    "Note: You are %s hour behind server time.": [
      "Nota: O use fuso hor\u00e1rio est\u00e1 %s hora atrasado em rela\u00e7\u00e3o ao servidor.",
      "Nota: O use fuso hor\u00e1rio est\u00e1 %s horas atrasado em rela\u00e7\u00e3o ao servidor.",
      "",
      "",
      "",
      ""
    ],
    "Notification": "Notifica\u00e7\u00e3o",
    "November": "Novembro",
    "Now": "Agora",
    "Observer": "Observador",
    "October": "Outubro",
    "Only alphanumeric characters and spaces allowed": "\u00c9 permitido somente caracteres alfanum\u00e9ricos e espa\u00e7os",
    "Participant": "Participante",
    "Participants": "Participantes",
    "Please enter new template name!": "Insira novo nome do template!",
    "Please enter preview email!": "Insira visualiza\u00e7\u00e3o do e-mail!",
    "Please enter updated template name or leave the old one!": "Insira nome do template atualizado ou mantenha o nome antigo!",
    "Please select at least one course": "Selecione no m\u00ednimo um curso",
    "Please select at least one student": "Selecione no m\u00ednimo um aluno",
    "Please select file first.": "Selecione o arquivo primeiro.",
    "Please select file for upload.": "Selecione arquivo para upload.",
    "Please select project": "Selecione o projeto",
    "Poll/Survey Question": "Pergunta do enquete/pesquisa",
    "Preview Email!": "Visualizar e-mail!",
    "Proficiency": "Profici\u00eancia",
    "Program": "Programa",
    "Progress": "Progresso",
    "Progress : 0%": "Progresso: 0%",
    "Progress: %(progress)s %": "Progresso: %(progress)s %",
    "Progress: %(value)s%": "Progresso: %(value)s%",
    "Remove": "Remover",
    "Remove all": "Remover todos",
    "Report of bulk update will be sent to your email.": "O relat\u00f3rio da atualiza\u00e7\u00e3o em massa ser\u00e1 enviado para o seu e-mail.",
    "Request Time": "Tempo necess\u00e1rio",
    "Save Changes": "Salvar altera\u00e7\u00f5es",
    "Search by Keyword": "Pesquisar por palavra-chave",
    "Select Course": "Selecionar curso",
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "Selecionados: %(selected)s, Sucesso: %(successful)s, Falha: %(failed)s",
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "Selecionados: %(selectedRows)s, Sucesso: 0, Falha: 0",
    "Send": "Enviar",
    "Send Course Intro Email": "Enviar e-mail de introdu\u00e7\u00e3o ao curso",
    "September": "Setembro",
    "Show": "Mostrar",
    "Show Errors": "Mostrar erros",
    "Show password": "Ocultar senha",
    "Start": "In\u00edcio",
    "Start time": "Hora de in\u00edcio",
    "Status": "Status",
    "Successful": "Com \u00eaxito",
    "Successfully Enrolled in 1 Course": "Sucesso na inscri\u00e7\u00e3o em 1 curso",
    "Successfully added new template!": "Novo template adicionado com sucesso!",
    "Successfully deleted template!": "Template exclu\u00eddo com sucesso!",
    "Successfully sent email!": "E-mail enviado com sucesso!",
    "Successfully sent preview email!": "E-mail de visualiza\u00e7\u00e3o enviado com sucesso!",
    "Successfully updated template!": "Template atualizado com sucesso!",
    "TA": "TA",
    "Task failed to execute. Please retry later.": "A tarefa n\u00e3o foi executada. Tente novamente mais tarde.",
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "O arquivo .csv tem mais de %(limit)s linhas: %(lines)s, divida-o em mais arquivos!",
    "The content takes place in a new window.": "O conte\u00fado aparecer em uma nova janela.",
    "There was an error submitting your file.": "Ocorreu um erro ao enviar seu arquivo.",
    "This app name cannot contain non-alphanumeric characters!": "O nome do aplicativo deve conter apenas caracteres alfanum\u00e9ricos!",
    "This app name cannot have more than 30 characters!": "O nome do aplicativo deve ter no m\u00e1ximo 30 caracteres!",
    "This company name cannot contain non-alphanumeric characters!": "O nome da empresa deve conter apenas caracteres alfanum\u00e9ricos!",
    "This company name cannot have more than 30 characters!": "O nome da empresa deve ter no m\u00e1ximo 30 caracteres!",
    "This field is required.": "Este campo \u00e9 obrigat\u00f3rio.",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Esta \u00e9 a lista de %s dispon\u00edveis. Poder\u00e1 escolher alguns, selecionando-os na caixa abaixo e clicando na seta \"Escolher\" entre as duas caixas.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Esta \u00e9 a lista de %s escolhidos. Poder\u00e1 remover alguns, selecionando-os na caixa abaixo e clicando na seta \"Remover\" entre as duas caixas.",
    "This tag name cannot contain non-alphanumeric characters!": "O nome da tag deve conter apenas caracteres alfanum\u00e9ricos!",
    "This tag name cannot have more than 30 characters!": "O nome da tag deve ter no m\u00e1ximo 30 caracteres!",
    "Today": "Hoje",
    "Today at ": "hoje",
    "Tomorrow": "Amanh\u00e3",
    "Try selecting your company from the type-ahead results.": "Tente selecionar a sua empresa a partir dos resultados de preenchimento autom\u00e1tico.",
    "Type into this box to filter down the list of available %s.": "Digite nesta caixa para filtrar a lista de %s dispon\u00edveis.",
    "Unenroll": "Cancelar a inscri\u00e7\u00e3o",
    "Unenroll Participants": "Cancelar a inscri\u00e7\u00e3o de participantes",
    "Unenroll all selected participants from this course?": "Cancelar a inscri\u00e7\u00e3o de todos os participantes selecionados neste curso?",
    "Updated user data!": "Dados do usu\u00e1rio atualizados!",
    "Urban Airship URL": "URL do Urban Airship",
    "User successfully enrolled in course": "Usu\u00e1rio inscrito no curso com sucesso",
    "User will be enrolled in course selected below.": "O usu\u00e1rio ser\u00e1 inscrito no curso selecionado abaixo.",
    "Username": "Nome de usu\u00e1rio",
    "Username can't be empty! ": "O nome de usu\u00e1rio n\u00e3o pode estar vazio!",
    "View Details": "Visualizar detalhes",
    "We'll e-mail you when your report is ready to download.": "Enviaremos um e-mail quando seu relat\u00f3rio estiver pronto para download.",
    "Webinar": "Webin\u00e1rio",
    "Welcome to McKinsey Academy": "Bem-vindo ao McKinsey Academy",
    "What would you like to do now?": "O que deseja fazer agora?",
    "Yesterday": "Ontem",
    "You are about to delete email template. Are you sure?": "Voc\u00ea est\u00e1 prestes a excluir o template de e-mail. Tem certeza que deseja continuar?",
    "You are now": "Agora voc\u00ea \u00e9 o",
    "You can only add up to 4 fields": "Voc\u00ea pode adicionar no m\u00e1ximo 4 campos",
    "You don't have permission to create a new tag, please select one from the list!": "Voc\u00ea n\u00e3o tem permiss\u00e3o para criar uma nova tag, selecione uma tag na lista!",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Selecionou uma a\u00e7\u00e3o mas ainda n\u00e3o guardou as mudan\u00e7as dos campos individuais. Provavelmente querer\u00e1 o bot\u00e3o Ir ao inv\u00e9s do bot\u00e3o Guardar.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Selecionou uma a\u00e7\u00e3o mas ainda n\u00e3o guardou as mudan\u00e7as dos campos individuais. Carregue em OK para gravar. Precisar\u00e1 de correr de novo a a\u00e7\u00e3o.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Tem mudan\u00e7as por guardar nos campos individuais. Se usar uma a\u00e7\u00e3o, as suas mudan\u00e7as por guardar ser\u00e3o perdidas.",
    "You need to enter course ID!": "Voc\u00ea deve inserir a ID do curso!",
    "You need to enter name!": "Voc\u00ea deve inserir o nome!",
    "You need to select at least one participant to be able to apply bulk actions.": "Voc\u00ea deve selecionar no m\u00ednimo um participante para poder aplicar a\u00e7\u00f5es m\u00faltiplas.",
    "You need to select course!": "Voc\u00ea deve selecionar o curso!",
    "You need to select status!": "Voc\u00ea deve selecionar o status!",
    "You were logged out due to inactivity. Please log back in to continue.": "Voc\u00ea foi desconectado devido a inatividade. Entre novamente para continuar.",
    "Your Progress: %(value)s%": "Seu progresso: %(value)s%",
    "Your course begins in %(days)s day.": [
      "Seu curso come\u00e7a em %(days)s dia.",
      "Seu curso come\u00e7a em %(days)s dias.",
      "Seu curso come\u00e7a em %(days)s dias.",
      "Seu curso come\u00e7a em %(days)s dias.",
      "Seu curso come\u00e7a em %(days)s dias.",
      "Seu curso come\u00e7a em %(days)s dias."
    ],
    "Your course hasn't begun yet. ": "Seu curso ainda n\u00e3o come\u00e7ou.",
    "complete": "completo",
    "contains %s learner": [
      "cont\u00e9m %s aluno",
      "cont\u00e9m %s alunos",
      "cont\u00e9m %s alunos",
      "cont\u00e9m %s alunos",
      "cont\u00e9m %s alunos",
      "cont\u00e9m %s alunos"
    ],
    "course id": "id do curso",
    "email": "e-mail",
    "for": "em",
    "iOS DL URL": "URL do iOS DL",
    "in the cohort!": "na coorte!",
    "location": "localiza\u00e7\u00e3o",
    "one letter Friday\u0004F": "S",
    "one letter Monday\u0004M": "S",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "Q",
    "one letter Tuesday\u0004T": "T",
    "one letter Wednesday\u0004W": "Q",
    "same as your organization's average": "igual \u00e0 m\u00e9dia da sua organiza\u00e7\u00e3o",
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
    "DATETIME_FORMAT": "j \\d\\e F \\d\\e Y \u00e0\\s H:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d",
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%Y",
      "%d/%m/%y %H:%M:%S",
      "%d/%m/%y %H:%M:%S.%f",
      "%d/%m/%y %H:%M",
      "%d/%m/%y"
    ],
    "DATE_FORMAT": "j \\d\\e F \\d\\e Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%d/%m/%Y",
      "%d/%m/%y"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 0,
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

