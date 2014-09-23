# Configuring programs, clients and courses

One can use preconfigured devstack users to log into Apros and view all courses available to them, but:

* One should use username instead of email (e.g. for `staff@example.com` it's `staff`).
* Before viewing any courses one need to configure Apros itself to allow students viewing courses. Failing to do so might
result in undefined behavior ranging from no courses available to DB-related crashes.

# Navigating admin panel

There are two navigation panels in Apros admin: always visible top menu and sub menu, which appear on some of the pages and 
does not strike to the eye. Submenu appears on the page itself and not outlined/highlighted/emphasized in any other way, except for 
being in ALL CAPS CASE and usually containing `OVERVIEW` item.

In order to avoid possible misreadings, regardless of actual case

* top menu items will be referenced in `ALL CAPS`
* sub menu items will be referenced in `Title Case`
* page buttons will be refernced as `Normal case`

# Logging into admin panel

In order to configure Apros one need to log in into Apros admin panel. Seed data contains default set of users, 
some of which are admins, e.g. `mcka_admin_user`. All users share same [default password][load-seed-data] `PassworD12!@`. So, in order to get into 
admin backend, log into Apros as mcka_admin_user / PassworD12!@. You should see `MCKA ADMIN` item in top menu, which leads to admin panel.

[load-seed-data]: https://github.com/mckinseyacademy/mcka_apros/blob/master/main/management/commands/load_seed_data.py#L36-L55

# Configuring programs

Navigate to `PROGRAMS` via top menu, click `Add program`. Give it a name and display name, choose beginning and end date. Date ranges that does not include 
current date allows student to review courseware, but does not track it progress, so play safe and include current date in date range. Click `Save program`.

To add courses to program click `Assign Courses to the Program` from submenu. You should see a list of all 
courses available in LMS (two demo courses for vanilla devstack). No checkboxes on that page, courses added to selection are highlighted 
only. Clicking `Move selected courses into program` will add them to program.

# Creating and configuring client

Navigate to `CLIENTS`, click `Add client`. Fill in all fields as all of them are required, click `Save Client`.

Tricky part is that you can't just create and assign students to client - you must import them via CSV. CSV format is the following (extracted from 
[mcka_apros/admin/controller.py][admin-controller] -> _process_line):

    # format is Email, FirstName, LastName, Title, City, Country (last 3 are optional)

Default separator is used, first line **is skipped unconditionally**, e.g. both

    Email, FirstName, LastName, Title, City, Country
    user2@localhost.org,User2Name,User2LastName

and 

    user1@localhost.org,User1Name,User1LastName
    user2@localhost.org,User2Name,User2LastName

will yield **one** user with `Email=user2@localhost.org`. Note that you can't reuse existing emails, as new users are created in LMS for each 
student. Make sure LMS is up and you can access tty where it's running as new accounts require activation, which is sent via email. Luckily,
emails are visible in console instance running LMS, so you don't have to set up smtp server and provide actual emails.

Upon account activation you will be asked to provide password and username for new user, as well as correct Title, City and Country, **but not
Email, First Name and Last Name**, they are set in stone.

If you followed a link in activation email you are likely to be logged in as new user. Log out and log back in as admin, and get back to the admin panel.

In order to access any course materials, student must be assigned to the course via admin panel, no self-enrollment allowed.
To assign user to course you first assign it to the program by navigating to `CLIENTS`, clicking on the client under which we registered target student
and than going to `Assign Students To Program`.

Select student in the table, select program in right-hand side panel, click `Move selected students into program`. Than navigate to `Assign Students To
Courses`, select user, select program, check checkboxes for courses to be accessible by the student, click `Move selected students to Course(s)`. 

Note that neither existing student-program nor student-course links are not shown in any way. However, those operation are idempotent, so it would not
cause any harm to add a student to the same program/course several times. Also, there's no option to unenroll, so not checking some courses student already 
been added to won't result in unenrolling from them.

To verify you have succeed, log in as student and make sure you have a blue menu reading the name of the course to the left and a set of 
buttons to the right. If you can see it, clicking on the first icon (computer one) will show dropdown menu with a list of lessons in selected course.
You can change the course by clicking "four squares" icon to the left of course name.

[admin-controller]: https://github.com/mckinseyacademy/mcka_apros/blob/master/admin/controller.py#L148