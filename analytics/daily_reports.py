from django.db import connections
from django.conf import settings
import xlsxwriter
import csv
from email.mime.text import MIMEText
from datetime import date
import smtplib
import datetime
from collections import defaultdict
import smtplib,email,email.encoders,email.mime.text,email.mime.base
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import sys
import os

#send email with course name and file
def send_email(course_name, file_name):
	try:
		msg = MIMEMultipart(settings.DAILY_EMAIL_REPORTS_CONFIG['data'])
		msg['Subject'] = "Report for " + course_name + " %s" % (date.today().strftime(settings.DAILY_EMAIL_REPORTS_CONFIG['date_format']))
		msg['To'] = settings.DAILY_EMAIL_REPORTS_CONFIG['email_to']
		msg['From'] = settings.DAILY_EMAIL_REPORTS_CONFIG['email_from']
		fp = open(settings.DAILY_EMAIL_REPORTS_CONFIG['output_directory']+file_name, 'rb')
		file_excel=email.mime.base.MIMEBase('application','vnd.ms-excel')
		file_excel.set_payload(fp.read())
		fp.close()
		email.encoders.encode_base64(file_excel)
		file_excel.add_header('Content-Disposition','attachment;filename='+course_name+str(datetime.date.today())+settings.DAILY_EMAIL_REPORTS_CONFIG['file_format'])
		msg.attach(file_excel)
		#TODO: add message body in email if needed.
		mail = smtplib.SMTP(settings.DAILY_EMAIL_REPORTS_CONFIG['smtp_server'], settings.DAILY_EMAIL_REPORTS_CONFIG['smtp_port'])
		mail.starttls()
		mail.login(settings.DAILY_EMAIL_REPORTS_CONFIG['smtp_user_email'], settings.DAILY_EMAIL_REPORTS_CONFIG['smtp_user_password'])
		mail.sendmail(settings.DAILY_EMAIL_REPORTS_CONFIG['email_from'], settings.DAILY_EMAIL_REPORTS_CONFIG['email_from'], msg.as_string())
		mail.quit()
	except Exception,e:
		sys.stdout.write("Error sending email")
		sys.stdout.write(str(e))
	else:
		sys.stdout.write("Email Sent")
		#if email is sent, remove file from output directory
		os.remove(settings.DAILY_EMAIL_REPORTS_CONFIG['output_directory']+file_name)


#build output xls sheet using xlsxwriter
def writetoxlsxwriter(file_name, column_names, rows, total_exercises):
	#createworksheet
	workbook = xlsxwriter.Workbook(file_name)
	worksheet = workbook.add_worksheet()
	#worksheet presentation
	#set column size
	worksheet.set_column('A:A', 10)
	worksheet.set_column('B:B', 10)
	worksheet.set_column('C:C', 10)
	worksheet.set_column('D:D', 10)
	worksheet.set_column('E:E', 30)
	worksheet.set_column('F:F', 20)
	worksheet.set_column('G:G', 20)
	worksheet.set_column('H:H', 20)
	worksheet.set_column('I:I', 20)
	worksheet.set_column('J:J', 20)
	worksheet.set_column('O:O', 20)
	worksheet.set_column('P:P', 10)
	worksheet.set_column('Q:Q', 10)
	worksheet.set_column('R:R', 10)
	# Add format for cells.
	bold = workbook.add_format({'bold': True})
	number_format = workbook.add_format({'num_format': '###0'})
	date_format = workbook.add_format({'num_format': 'mm/dd/yy'})
	# output all titles
	row = 0
	col = 0
	for names in column_names:
		#output column names to spreadsheet
		worksheet.write(row, col, names, bold )
		col += 1
	#output results to spreadsheet
	row_results = 0
	for results_data in rows:
		col_results = 0
		row_results += 1
		for item_data in results_data:
			if(col_results == 0 or col_results == 5 or col_results == 9):
				worksheet.write_number(row_results, col_results, int(item_data), number_format)
			else:
				worksheet.write(row_results, col_results, item_data)
			
			col_results += 1
	#get total rows
	total_rows =  row_results + 1 
	#######
	#######ENGAGEMENT FUNNEL######
	#######
	worksheet.write(2, 14, 'Engagement Funnel', bold)
	worksheet.write(3, 15, '# people', bold)
	worksheet.write(3, 16, '% invited', bold)
	worksheet.write(3, 17, '% activated', bold)
	worksheet.write(4, 14, 'Invited')
	worksheet.write(5, 14, 'Activated')
	worksheet.write(6, 14, 'Engaged')
	worksheet.write(7, 14, 'Engaged last 7 days')
	#Invited/Activated/Engaged/Engaged past 7 days
	#First column - number of people invited/activated/engaged/engaged past 7 days.
	worksheet.write_formula(4, 15, '=COUNTA(E2:E'+str(total_rows)+')') #number of people invited => total_rows
	worksheet.write_formula(5, 15, '=SUM(F2:F'+str(total_rows)+')') #number of people activated => add activations 
	worksheet.write_formula(6, 15, '=COUNTIF(J2:J'+str(total_rows)+',">0")') #number of people that have engagement greater than one. 
	worksheet.write_formula(7, 15, '=Q30') #total number of people that have engaged in the past 7 days
	#Second Column - percent of people invited/activated/engaged/engaged past 7 days.
	worksheet.write_formula(5, 16, '=ROUNDUP(P6/$P$5*100, 0)') #percent of people activated/people invited
	worksheet.write_formula(6, 16, '=ROUNDUP(P7/$P$5*100, 0)') #percent of people engaged/people invited
	worksheet.write_formula(7, 16, '=ROUNDUP(P8/$P$5*100, 0)') #percent of people engaged last 7 days/people invited
	#Third column - Engagement of people who have activated
	worksheet.write_formula(6, 17, '=ROUNDUP(P7/$P$6*100, 0)')
	worksheet.write_formula(7, 17, '=ROUNDUP(P8/$P$6*100, 0)')
	#######
	#######PROGRESS SUMMARY######
	#######
	worksheet.write(9, 14, 'Progress Summary', bold)
	worksheet.write(10, 15, '# of exercises', bold)
	worksheet.write(10, 16, '% complete', bold)
	worksheet.write(11, 14, 'Maximum')
	worksheet.write(12, 14, 'Top Quartile')
	worksheet.write(13, 14, 'Average')
	worksheet.write(14, 14, 'Bottom Quartile')
	#First Column - Progress - number of exercises and completed by user: MAX, Top Quartile, Bottom Quartile, Average.
	worksheet.write_formula(11, 15, '=MAX($J$2:$J$'+str(total_rows)+')') #max number of exercises a student has engaged with.
	worksheet.write_formula(12, 15, '=QUARTILE($J$2:$J$'+str(total_rows)+',3)') #Top Quartile of number of exercises a student has engaged with.
	worksheet.write_formula(13, 15, '=AVERAGE($J$2:$J$'+str(total_rows)+')') #Average of number of exercises a student has engaged with
	worksheet.write_formula(14, 15, '=QUARTILE($J$2:$J$'+str(total_rows)+',1)') #Bottom Quartile of number of exercises a student has engaged with.
	#Second Column - Progress - Percent completeness per max number of exercises
	worksheet.write_formula(11, 16, '=ROUNDUP(P12/$P$33*100, 0)') #max
	worksheet.write_formula(12, 16, '=ROUNDUP(P13/$P$33*100, 0)') #top quartile
	worksheet.write_formula(13, 16, '=ROUNDUP(P14/$P$33*100, 0)') #average
	worksheet.write_formula(14, 16, '=ROUNDUP(P15/$P$33*100, 0)') #bottom quartile
	#######
	#######ENGAGEMENT DETAIL ######
	#######
	#######
	#build tables
	worksheet.write(17, 14, 'Engagement Detail', bold)
	worksheet.write(18, 14, 'Todays date')
	worksheet.write(20, 14, 'Date', bold)
	worksheet.write(20, 15, '# of days', bold)
	worksheet.write(20, 16, '# of people', bold)
	worksheet.write(20, 17, '% activated', bold)
	worksheet.write(20, 18, 'cumulative', bold)
	#actual days
	worksheet.write(21, 15, '0')
	worksheet.write(22, 15, '1')
	worksheet.write(23, 15, '2')
	worksheet.write(24, 15, '3')
	worksheet.write(25, 15, '4')
	worksheet.write(26, 15, '5')
	worksheet.write(27, 15, '6')
	worksheet.write(28, 15, '7')	
	#Todays date
	worksheet.write_formula(18, 15, '=TODAY()', date_format)
	#First Column - Dates
	worksheet.write_formula(21, 14, '=$P$19-P22', date_format)
	worksheet.write_formula(22, 14, '=$P$19-P23', date_format)
	worksheet.write_formula(23, 14, '=$P$19-P24', date_format)
	worksheet.write_formula(24, 14, '=$P$19-P25', date_format)
	worksheet.write_formula(25, 14, '=$P$19-P26', date_format)
	worksheet.write_formula(26, 14, '=$P$19-P27', date_format)
	worksheet.write_formula(27, 14, '=$P$19-P28', date_format)
	worksheet.write_formula(28, 14, '=$P$19-P29', date_format)
	#Third Column - number of people who's most recent login has been in the past 7 days
	worksheet.write_formula(21, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O21)')
	worksheet.write_formula(22, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O22)')
	worksheet.write_formula(23, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O23)')
	worksheet.write_formula(24, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O24)')
	worksheet.write_formula(25, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O25)')
	worksheet.write_formula(26, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O26)')
	worksheet.write_formula(27, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O27)')
	worksheet.write_formula(28, 16, '=COUNTIF($G$2:$G$'+str(total_rows)+',"="&O28)')
	worksheet.write_formula(29, 16, '=SUM(Q22:Q29)')
	#Fourth Column - number of people who have activated in the past 7 days
	worksheet.write_formula(21, 17, '=ROUNDUP(Q22/$P$6*100, 0)')
	worksheet.write_formula(22, 17, '=ROUNDUP(Q23/$P$6*100, 0)')
	worksheet.write_formula(23, 17, '=ROUNDUP(Q24/$P$6*100, 0)')
	worksheet.write_formula(24, 17, '=ROUNDUP(Q25/$P$6*100, 0)')
	worksheet.write_formula(25, 17, '=ROUNDUP(Q26/$P$6*100, 0)')
	worksheet.write_formula(26, 17, '=ROUNDUP(Q27/$P$6*100, 0)')
	worksheet.write_formula(27, 17, '=ROUNDUP(Q28/$P$6*100, 0)')
	worksheet.write_formula(28, 17, '=ROUNDUP(Q29/$P$6*100, 0)')
	worksheet.write_formula(29, 17, '=ROUNDUP(Q30/$P$6*100, 0)')
	#Fifth Column - Cumulative activation per day
	worksheet.write_formula(21, 18, '=R22')
	worksheet.write_formula(22, 18, '=S22+R23')
	worksheet.write_formula(23, 18, '=S23+R24')
	worksheet.write_formula(24, 18, '=S24+R25')
	worksheet.write_formula(25, 18, '=S25+R26')
	worksheet.write_formula(26, 18, '=S26+R27')
	worksheet.write_formula(27, 18, '=S27+R28')
	worksheet.write_formula(28, 18, '=S28+R29')
	worksheet.write_formula(29, 18, '=S29+R30')
	#######
	####### PROGRESS DETAIL #######
	#######
	worksheet.write(31, 14, 'Progress Detail', bold)
	worksheet.write(32, 14, 'Total # of exercises')		
	worksheet.write(34, 14, '% complete', bold)
	worksheet.write(34, 15, '# exercises', bold)
	worksheet.write(34, 16, '# of people', bold)
	worksheet.write(34, 17, '% activated', bold)
	#total of exercises
	worksheet.write(32, 15, total_exercises)	
	#First Column - Percent Complete
	worksheet.write(35, 14, '10% complete')
	worksheet.write(36, 14, '20% complete')
	worksheet.write(37, 14, '30% complete')
	worksheet.write(38, 14, '40% complete')
	worksheet.write(39, 14, '50% complete')
	worksheet.write(40, 14, '60% complete')
	worksheet.write(41, 14, '70% complete')
	worksheet.write(42, 14, '80% complete')
	worksheet.write(43, 14, '90% complete')
	worksheet.write(44, 14, '100% complete')
	#Second column - Percent distribution of number of exercises complete out of total number of exercises
	worksheet.write_formula(35, 15, '=ROUNDDOWN($P$33*10%,0)')
	worksheet.write_formula(36, 15, '=ROUNDDOWN($P$33*20%,0)')
	worksheet.write_formula(37, 15, '=ROUNDDOWN($P$33*30%,0)')
	worksheet.write_formula(38, 15, '=ROUNDDOWN($P$33*40%,0)')
	worksheet.write_formula(39, 15, '=ROUNDDOWN($P$33*50%,0)')
	worksheet.write_formula(40, 15, '=ROUNDDOWN($P$33*60%,0)')
	worksheet.write_formula(41, 15, '=ROUNDDOWN($P$33*70%,0)')
	worksheet.write_formula(42, 15, '=ROUNDDOWN($P$33*80%,0)')
	worksheet.write_formula(43, 15, '=ROUNDDOWN($P$33*90%,0)')
	worksheet.write_formula(44, 15, '=ROUNDDOWN($P$33*100%,0)')
	#Third column - number of people that have engaged (completed lessons) greater than percent distribution of exercises  
	worksheet.write_formula(35, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P36)')
	worksheet.write_formula(36, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P37)')
	worksheet.write_formula(37, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P38)')
	worksheet.write_formula(38, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P39)')
	worksheet.write_formula(39, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P40)')
	worksheet.write_formula(40, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P41)')
	worksheet.write_formula(41, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P42)')
	worksheet.write_formula(42, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P43)')
	worksheet.write_formula(43, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P44)')
	worksheet.write_formula(44, 16, '=COUNTIF($J$2:$J$'+str(total_rows)+',">="&P45)')
	#Fourth Column - percent of people activated in percent distribution of exercises
	worksheet.write_formula(35, 17, '=ROUNDUP(Q36/$P$6*100, 0)')
	worksheet.write_formula(36, 17, '=ROUNDUP(Q37/$P$6*100, 0)')
	worksheet.write_formula(37, 17, '=ROUNDUP(Q38/$P$6*100, 0)')
	worksheet.write_formula(38, 17, '=ROUNDUP(Q39/$P$6*100, 0)')
	worksheet.write_formula(39, 17, '=ROUNDUP(Q40/$P$6*100, 0)')
	worksheet.write_formula(40, 17, '=ROUNDUP(Q41/$P$6*100, 0)')
	worksheet.write_formula(41, 17, '=ROUNDUP(Q42/$P$6*100, 0)')
	worksheet.write_formula(42, 17, '=ROUNDUP(Q43/$P$6*100, 0)')
	worksheet.write_formula(43, 17, '=ROUNDUP(Q44/$P$6*100, 0)')
	worksheet.write_formula(44, 17, '=ROUNDUP(Q45/$P$6*100, 0)')
	worksheet.write_formula(5, 15, '=SUM(F2:F'+str(total_rows)+')') 
	worksheet.write_formula(6, 16, '=ROUNDUP(P7/$P$5*100, 0)')
	worksheet.write_formula(7, 16, '=ROUNDUP(P8/$P$5*100, 0)')
	#
	workbook.close()

#execute sql query
def execute_sql(schema_name, sql_statement):
	#initialization
	result = []
	try:
		#queries against edx database
		cursor = connections[schema_name].cursor()
		#execute sql
		cursor.execute(sql_statement)
		#encode and structure data for writing to file
		columns = [d[0] for d in cursor.description]
	except Exception, e:
		sys.stdout.write("SQL error")
		sys.stdout.write(str(e))
	else:
		#print columns
		row = cursor.fetchone()
		#print row
		while (row != None):
			result.append([str(cell).encode("utf-8") for cell in row])
			row = cursor.fetchone()
		results = defaultdict(list)
		results['columns'].append(columns)
		results['result'].append(result)
	
		return results

#build query for get active courses
def get_reporting_courses():
	sql_active = ' SELECT course_id, total_exercises FROM active_courses WHERE is_active = 1'
	return sql_active

#build query for course dataset
def build_course_dataset_query(course_name):
	sql = list()
	sql.append(' SELECT au.id as "User ID", au.username as "Username",au.first_name as "First Name",au.last_name as "Last Name", au.email as "Email",sce.is_active as "Activated",')
	sql.append('DATE_FORMAT(au.last_login, "%c/%d/%Y") as "Most Recent Login",') 
	sql.append('DATE_FORMAT(au.date_joined, "%c/%d/%Y") as "Activation Date",')
	sql.append('DATE_FORMAT(sce.created, "%c/%d/%Y") as "Enrollment Date", ')
	sql.append('(Select count(*) from api_manager_coursemodulecompletion api where api.user_id = au.id AND api.stage IS null')
	sql.append(' AND api.course_id = "'+course_name+'") as "Exercise Engagement"') 
	sql.append(' FROM student_courseenrollment as sce ')
	sql.append(' left join auth_user as au ON au.id = sce.user_id ')
	sql.append(' WHERE course_id = "'+course_name+'" ')
	sql.append(' and sce.is_active = 1 AND au.id NOT IN (Select sc.user_id from student_courseaccessrole as sc')
	sql.append(' WHERE sc.course_id = "'+course_name+'")')
	sql.append(' ORDER BY au.id')
	return "".join(sql)

#run script - get active courses, query dataset, output to excel and email. 

#build query to get active courses from apros - get active courses
active_courses_query = get_reporting_courses()
active_courses_dict = execute_sql(settings.DAILY_EMAIL_REPORTS_CONFIG['apros_db_name'], active_courses_query)

if active_courses_dict:
	#for each active course get course dataset and spit out into spreadsheet.
	for a_course in active_courses_dict['result'][0]:
		try:
			course_name = a_course[0]
			total_exercises = a_course[1]
			course_dataset_query = build_course_dataset_query(course_name)
			course_dict = execute_sql(settings.DAILY_EMAIL_REPORTS_CONFIG['edx_db_name'], course_dataset_query)
			file_name = course_name.replace('/','')+'_'+str(datetime.date.today())+settings.DAILY_EMAIL_REPORTS_CONFIG['file_format']
			if course_dict:
				#create excel spreadsheet with data and pivot tables.
				writetoxlsxwriter(settings.DAILY_EMAIL_REPORTS_CONFIG['output_directory']+file_name, course_dict['columns'][0], course_dict['result'][0], total_exercises)
				#email excel spreadsheet with data and pivot tables.
				send_email(course_name, file_name)
		except Exception, e:
			sys.stdout.write("Error sending course"+a_course[0])
			sys.stdout.write(str(e))
			pass 
		else:
			sys.stdout.write("Course sending successful!"+a_course[0])
else:
	sys.stdout.write("No active courses") 



