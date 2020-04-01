

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
    " day": " \u5929",
    " week": " \u5468",
    "# of people": "\u4eba\u6570",
    "% total cohort": "\u603b\u7fa4\u7ec4 %",
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s \u95e8\u8bfe\u7a0b\u5e26\u6709 %(tagDetails)s \u6807\u7b7e",
      "%(count)s \u95e8\u8bfe\u7a0b\u5e26\u6709 %(tagDetails)s \u6807\u7b7e",
      "",
      "",
      "",
      ""
    ],
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s  \u5728\u8bfe\u7a0b\u5f00\u59cb\u4e4b\u524d\uff0c\u60a8\u53ef\u4ee5\u6d4f\u89c8\u672c\u7f51\u7ad9\u4e86\u89e3\u66f4\u591a\u6709\u5173\u8bfe\u7a0b\u5185\u5bb9\u7684\u4fe1\u606f\u3002",
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "%(selectedRows)s \u540d\u53c2\u4e0e\u8005\u5c06\u6ce8\u518c\u53c2\u52a0\u4ee5\u4e0b\u9009\u5b9a\u8bfe\u7a0b\u3002",
      "%(selectedRows)s \u540d\u53c2\u4e0e\u8005\u5c06\u6ce8\u518c\u53c2\u52a0\u4ee5\u4e0b\u9009\u5b9a\u8bfe\u7a0b\u3002",
      "",
      "",
      "",
      ""
    ],
    "%(value)s%": "%(value)s%",
    "%s invalid email was ignored.": [
      "%s \u4e2a\u65e0\u6548\u90ae\u7bb1\u5df2\u88ab\u5ffd\u7565\u3002",
      "%s \u4e2a\u65e0\u6548\u90ae\u7bb1\u5df2\u88ab\u5ffd\u7565\u3002",
      "%s \u4e2a\u65e0\u6548\u90ae\u7bb1\u5df2\u88ab\u5ffd\u7565\u3002",
      "%s \u4e2a\u65e0\u6548\u90ae\u7bb1\u5df2\u88ab\u5ffd\u7565\u3002",
      "%s \u4e2a\u65e0\u6548\u90ae\u7bb1\u5df2\u88ab\u5ffd\u7565\u3002",
      "%s \u4e2a\u65e0\u6548\u90ae\u7bb1\u5df2\u88ab\u5ffd\u7565\u3002"
    ],
    "%s learner has been added to this cohort.": [
      "%s \u4e2a\u5b66\u5458\u5df2\u6dfb\u52a0\u5230\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u6dfb\u52a0\u5230\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u6dfb\u52a0\u5230\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u6dfb\u52a0\u5230\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u6dfb\u52a0\u5230\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u6dfb\u52a0\u5230\u8be5\u7fa4\u7ec4\u3002"
    ],
    "%s learner has been moved to this cohort.": [
      "%s \u4e2a\u5b66\u5458\u5df2\u79fb\u81f3\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u79fb\u81f3\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u79fb\u81f3\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u79fb\u81f3\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u79fb\u81f3\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u5df2\u79fb\u81f3\u8be5\u7fa4\u7ec4\u3002"
    ],
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "%s \u4e2a\u5b66\u5458\u9884\u5148\u5206\u914d\u5230\u8be5\u7fa4\u7ec4\u3002\u8be5\u5b66\u5458\u5728\u6ce8\u518c\u8be5\u8bfe\u7a0b\u65f6\u5c06\u81ea\u52a8\u52a0\u5165\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u9884\u5148\u5206\u914d\u5230\u8be5\u7fa4\u7ec4\u3002\u8be5\u5b66\u5458\u5728\u6ce8\u518c\u8be5\u8bfe\u7a0b\u65f6\u5c06\u81ea\u52a8\u52a0\u5165\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u9884\u5148\u5206\u914d\u5230\u8be5\u7fa4\u7ec4\u3002\u8be5\u5b66\u5458\u5728\u6ce8\u518c\u8be5\u8bfe\u7a0b\u65f6\u5c06\u81ea\u52a8\u52a0\u5165\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u9884\u5148\u5206\u914d\u5230\u8be5\u7fa4\u7ec4\u3002\u8be5\u5b66\u5458\u5728\u6ce8\u518c\u8be5\u8bfe\u7a0b\u65f6\u5c06\u81ea\u52a8\u52a0\u5165\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u9884\u5148\u5206\u914d\u5230\u8be5\u7fa4\u7ec4\u3002\u8be5\u5b66\u5458\u5728\u6ce8\u518c\u8be5\u8bfe\u7a0b\u65f6\u5c06\u81ea\u52a8\u52a0\u5165\u8be5\u7fa4\u7ec4\u3002",
      "%s \u4e2a\u5b66\u5458\u9884\u5148\u5206\u914d\u5230\u8be5\u7fa4\u7ec4\u3002\u8be5\u5b66\u5458\u5728\u6ce8\u518c\u8be5\u8bfe\u7a0b\u65f6\u5c06\u81ea\u52a8\u52a0\u5165\u8be5\u7fa4\u7ec4\u3002"
    ],
    "%s user was already in this cohort.": [
      "%s \u4e2a\u7528\u6237\u5df2\u7ecf\u5728\u8be5\u7fa4\u7ec4\u4e2d\u3002",
      "%s \u4e2a\u7528\u6237\u5df2\u7ecf\u5728\u8be5\u7fa4\u7ec4\u4e2d\u3002",
      "%s \u4e2a\u7528\u6237\u5df2\u7ecf\u5728\u8be5\u7fa4\u7ec4\u4e2d\u3002",
      "%s \u4e2a\u7528\u6237\u5df2\u7ecf\u5728\u8be5\u7fa4\u7ec4\u4e2d\u3002",
      "%s \u4e2a\u7528\u6237\u5df2\u7ecf\u5728\u8be5\u7fa4\u7ec4\u4e2d\u3002",
      "%s \u4e2a\u7528\u6237\u5df2\u7ecf\u5728\u8be5\u7fa4\u7ec4\u4e2d\u3002"
    ],
    "%s user/email was not found.": [
      "%s \u4e2a\u7528\u6237/\u90ae\u7bb1\u672a\u627e\u5230\u3002",
      "%s \u4e2a\u7528\u6237/\u90ae\u7bb1\u672a\u627e\u5230\u3002",
      "%s \u4e2a\u7528\u6237/\u90ae\u7bb1\u672a\u627e\u5230\u3002",
      "%s \u4e2a\u7528\u6237/\u90ae\u7bb1\u672a\u627e\u5230\u3002",
      "%s \u4e2a\u7528\u6237/\u90ae\u7bb1\u672a\u627e\u5230\u3002",
      "%s \u4e2a\u7528\u6237/\u90ae\u7bb1\u672a\u627e\u5230\u3002"
    ],
    ".0%": ".0%",
    "2 or more fields can not have the same name": "2 \u4e2a\u6216 2 \u4e2a\u4ee5\u4e0a\u5b57\u6bb5\u4e0d\u80fd\u540c\u540d",
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "<span class=\"green\">%(diff)s point</span> \u9ad8\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"green\">%(diff)s points</span> \u9ad8\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"green\">%(diff)s points</span> \u9ad8\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"green\">%(diff)s points</span> \u9ad8\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"green\">%(diff)s points</span> \u9ad8\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"green\">%(diff)s points</span> \u9ad8\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c"
    ],
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "<span class=\"green\">%(diff)s% </span> \u9ad8\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "<span class=\"red\"> %(diff)s point</span> \u4f4e\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"red\"> %(diff)s points</span> \u4f4e\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"red\"> %(diff)s points</span> \u4f4e\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"red\"> %(diff)s points</span> \u4f4e\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"red\"> %(diff)s points</span> \u4f4e\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
      "<span class=\"red\"> %(diff)s points</span> \u4f4e\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c"
    ],
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "<span class=\"red\"> %(diff)s% </span> \u4f4e\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
    "Activated": "\u5df2\u6fc0\u6d3b",
    "Activation File": "\u6fc0\u6d3b\u6587\u4ef6",
    "Activation Link": "\u6fc0\u6d3b\u94fe\u63a5",
    "Active": "\u6709\u6548",
    "Add new role e.g CEO,CTO": "\u589e\u52a0\u65b0\u89d2\u8272\uff0c\u4f8b\u5982 CEO\uff08\u9996\u5e2d\u6267\u884c\u5b98\uff09\u3001CTO\uff08\u9996\u5e2d\u6280\u672f\u5b98\uff09",
    "Admin Company": "\u7ba1\u7406\u516c\u53f8",
    "Admin Permissions": "\u7ba1\u7406\u6743\u9650",
    "All students added to private group have to be members of same company.": "\u6240\u6709\u52a0\u5165\u79c1\u4eba\u5c0f\u7ec4\u7684\u5b66\u5458\u5fc5\u987b\u96b6\u5c5e\u540c\u4e00\u5bb6\u516c\u53f8\u3002",
    "An error occurred submitting the request.": "\u63d0\u4ea4\u8bf7\u6c42\u65f6\u51fa\u9519\u3002",
    "Analytics URL": "Analytics URL",
    "Android DL URL": "Android \u4e0b\u8f7d URL",
    "Announcements": "\u516c\u544a",
    "App Name": "\u5e94\u7528\u540d\u79f0",
    "Are you sure you want to remove this ?": "\u662f\u5426\u786e\u5b9a\u8981\u5220\u9664\u6b64\u9879\uff1f",
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "\u786e\u5b9a\u8981\u5220\u9664\u8be5\u7ec4\uff1f \u8fd9\u4f1a\u5220\u9664\u4e0e\u8be5\u7ec4\u76f8\u5173\u7684\u63d0\u4ea4\u548c\u53cd\u9988\u3002",
    "Are you sure?": "\u786e\u5b9a\uff1f",
    "Assessment: %(label)s": "\u8bc4\u5b9a\uff1a%(label)s",
    "Avg Progress": "\u5e73\u5747\u8fdb\u5ea6",
    "Business Function": "\u804c\u80fd\u90e8\u95e8",
    "Business Unit": "\u4e8b\u4e1a\u90e8",
    "Change Status": "\u66f4\u6539\u72b6\u6001",
    "Change status of all selected participants to:": "\u5c06\u6240\u6709\u9009\u5b9a\u53c2\u4e0e\u8005\u7684\u72b6\u6001\u66f4\u6539\u4e3a\uff1a",
    "Check for Completion": "\u68c0\u67e5\u662f\u5426\u586b\u5199\u5b8c\u6574",
    "Click Add to specify Lesson Label": "\u5355\u51fb\u201c\u6dfb\u52a0\u201d\uff0c\u6307\u5b9a\u8bfe\u7a0b\u6807\u7b7e",
    "Click Add to specify Lessons Label": "\u5355\u51fb\u201c\u6dfb\u52a0\u201d\u6307\u5b9a\u8bfe\u7a0b\u6807\u7b7e",
    "Click Add to specify Module Label": "\u5355\u51fb\u201c\u6dfb\u52a0\u201d\uff0c\u6307\u5b9a\u6a21\u5757\u6807\u7b7e",
    "Click Add to specify Modules Label": "\u5355\u51fb\u201c\u6dfb\u52a0\u201d\u6307\u5b9a\u6a21\u5757\u6807\u7b7e",
    "Cohort": "\u7fa4\u7ec4",
    "Cohort Comp.": "\u7fa4\u7ec4\u6bd4\u8f83",
    "Company": "\u516c\u53f8",
    "Company Admin": "\u516c\u53f8\u7ba1\u7406\u5458",
    "Company ID": "\u516c\u53f8 ID",
    "Company doesn't exist! ": "\u516c\u53f8\u4e0d\u5b58\u5728\uff01",
    "Complete": "\u5b8c\u6210",
    "Complete all content to continue": "\u5b8c\u6574\u586b\u5199\u5185\u5bb9\u624d\u80fd\u7ee7\u7eed",
    "Complete all content to continue.": "\u5b8c\u6574\u586b\u5199\u5185\u5bb9\u624d\u80fd\u7ee7\u7eed",
    "Completed": "\u5df2\u5b8c\u6210",
    "Contains Errors": "\u5305\u542b\u9519\u8bef",
    "Content is complete, please continue.": "\u5185\u5bb9\u586b\u5199\u5b8c\u6574\uff0c\u8bf7\u7ee7\u7eed",
    "Couldn't add tag to course!": "\u65e0\u6cd5\u5c06\u6807\u7b7e\u6dfb\u52a0\u81f3\u8bfe\u7a0b\uff01",
    "Couldn't create new company!": "\u65e0\u6cd5\u521b\u5efa\u65b0\u516c\u53f8\uff01",
    "Couldn't create new tag!": "\u65e0\u6cd5\u521b\u5efa\u65b0\u6807\u7b7e\uff01",
    "Couldn't delete tag!": "\u65e0\u6cd5\u5220\u9664\u6807\u7b7e\uff01",
    "Couldn't delink App!": "\u65e0\u6cd5\u89e3\u9664\u4e0e\u5e94\u7528\u7a0b\u5e8f\u7684\u94fe\u63a5\uff01",
    "Couldn't link this App!": "\u65e0\u6cd5\u94fe\u63a5\u6b64\u5e94\u7528\u7a0b\u5e8f\uff01",
    "Country": "\u56fd\u5bb6/\u5730\u533a",
    "Course": "\u8bfe\u7a0b",
    "Course ID": "\u8bfe\u7a0b ID",
    "Course Name": "\u8bfe\u7a0b\u540d\u79f0",
    "Dashboard Name": "\u4eea\u8868\u677f\u540d\u79f0",
    "Date Added": "\u6dfb\u52a0\u65e5\u671f",
    "Delete Role": "\u5220\u9664\u89d2\u8272",
    "Deployment Mech": "\u90e8\u7f72\u673a\u5236",
    "Digital Content": "\u6570\u5b57\u5185\u5bb9",
    "Digital Course": "\u6570\u5b57\u8bfe\u7a0b",
    "Discussion": "\u8ba8\u8bba",
    "Do you really want to delete: \n": "\u662f\u5426\u786e\u5b9a\u8981\u5220\u9664\uff1a\n",
    "Download": "\u4e0b\u8f7d",
    "Download CSV File": "\u4e0b\u8f7d CSV \u6587\u4ef6",
    "Download Notifications CSV": "\u4e0b\u8f7d\u901a\u77e5 CSV",
    "Email": "\u7535\u5b50\u90ae\u4ef6",
    "Email Preview Success!": "\u7535\u5b50\u90ae\u4ef6\u9884\u89c8\u6210\u529f\uff01",
    "Email Success!": "\u7535\u5b50\u90ae\u4ef6\u53d1\u9001\u6210\u529f\uff01",
    "Email can't be empty! ": "\u7535\u5b50\u90ae\u4ef6\u4e0d\u80fd\u4e3a\u7a7a\uff01",
    "End": "\u7ed3\u675f",
    "End Date": "\u7ed3\u675f\u65e5\u671f",
    "End time": "\u7ed3\u675f\u65f6\u95f4",
    "Engagement": "\u53c2\u4e0e\u5ea6",
    "Enroll Participant": "\u6ce8\u518c\u53c2\u4e0e\u8005",
    "Enroll Participants": "\u6ce8\u518c\u53c2\u4e0e\u8005",
    "Enroll this list in another course": "\u5728\u53e6\u4e00\u95e8\u8bfe\u7a0b\u4e2d\u6ce8\u518c\u6b64\u5217\u8868",
    "Enrolled In": "\u5df2\u6ce8\u518c",
    "Error File": "\u9519\u8bef\u6587\u4ef6",
    "Error Occured!": "\u51fa\u73b0\u9519\u8bef\uff01",
    "Error initiating the report generation. Please retry later.": "\u521d\u59cb\u5316\u62a5\u544a\u751f\u6210\u65f6\u51fa\u9519\u3002\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
    "Error processing CSV file.": "\u5904\u7406 CSV \u6587\u4ef6\u65f6\u51fa\u9519\u3002",
    "Error uploading file. Please try again and be sure to use an accepted file format.": "\u4e0a\u4f20\u6587\u4ef6\u65f6\u51fa\u9519\u3002\u8bf7\u786e\u4fdd\u4f7f\u7528\u63a5\u53d7\u7684\u6587\u4ef6\u683c\u5f0f\uff0c\u7136\u540e\u91cd\u8bd5\u3002",
    "Export Report": "\u5bfc\u51fa\u62a5\u544a",
    "Exporting Stats for All Users": "\u5bfc\u51fa\u6240\u6709\u7528\u6237\u7684\u7edf\u8ba1\u6570\u636e",
    "Female": "\u5973",
    "Fetching data for file: %(filename)s": "\u6b63\u5728\u63d0\u53d6\u6587\u4ef6\u6570\u636e\uff1a%(filename)s",
    "File name": "\u6587\u4ef6\u540d",
    "File successfully uploaded!": "\u6587\u4ef6\u5df2\u6210\u529f\u4e0a\u4f20\uff01",
    "Filename": "\u7528\u6237\u540d",
    "First name can't be empty! ": "\u540d\u5b57\u4e0d\u80fd\u4e3a\u7a7a\uff01",
    "Go to %(course_id)s Course": "\u8f6c\u5230 %(course_id)s \u8bfe\u7a0b",
    "Grade": "\u8bc4\u5206",
    "Group Work": "\u7fa4\u7ec4\u5de5\u4f5c",
    "Group Work: %(label)s": "\u5c0f\u7ec4\u4f5c\u4e1a\uff1a%(label)s",
    "Group successfully updated": "\u5c0f\u7ec4\u5df2\u6210\u529f\u66f4\u65b0",
    "Group was not created": "\u5c0f\u7ec4\u672a\u521b\u5efa",
    "Group work": "\u5c0f\u7ec4\u4f5c\u4e1a",
    "Hide Details": "\u9690\u85cf\u8be6\u7ec6\u4fe1\u606f",
    "Hide password": "\u9690\u85cf\u5bc6\u7801",
    "I'm Done": "\u5df2\u5b8c\u6210",
    "Importing %(processed)s of %(total)s rows": "\u5bfc\u5165 %(processed)s of %(total)s \u5217",
    "Importing..": "\u5bfc\u5165\u2026",
    "In Person Session": "\u5f53\u9762\u6388\u8bfe",
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "\u5305\u62ec\u6bcf\u4e2a\u8bfe\u65f6\u7684\u8fdb\u5ea6\u660e\u7ec6\uff08\u6ce8\u610f\uff1a\u5bfc\u51fa\u5c06\u9700\u8981\u66f4\u591a\u65f6\u95f4\uff09",
    "Incomplete": "\u672a\u5b8c\u6210",
    "Initiated by": "\u53d1\u8d77\u4eba",
    "Invalid format for CSV file.": "CSV \u6587\u4ef6\u683c\u5f0f\u65e0\u6548\u3002",
    "It looks like you're not active. Click OK to keep working.": "\u60a8\u5df2\u957f\u65f6\u95f4\u65e0\u64cd\u4f5c\u3002\u5355\u51fb\u201c\u786e\u5b9a\u201d\u7ee7\u7eed\u3002",
    "It looks like your browser settings has pop-ups disabled.": "\u60a8\u7684\u6d4f\u89c8\u5668\u8bbe\u7f6e\u53ef\u80fd\u7981\u7528\u4e86\u5f39\u51fa\u7a97\u53e3\u3002",
    "Last Log In": "\u4e0a\u6b21\u767b\u5f55",
    "Last name can't be empty! ": "\u59d3\u6c0f\u4e0d\u80fd\u4e3a\u7a7a\uff01",
    "Launch pop-up to continue": "\u542f\u52a8\u5f39\u51fa\u7a97\u53e3\u4ee5\u7ee7\u7eed",
    "Leaderboards": "\u6392\u884c\u699c",
    "Learner email": "\u5b66\u5458\u90ae\u7bb1",
    "Lesson": "\u8bfe\u65f6",
    "Male": "\u7537",
    "Manager email": "\u7ba1\u7406\u8005\u90ae\u7bb1",
    "Moderator": "\u7248\u4e3b",
    "Module": "\u6a21\u5757",
    "Must be at least 8 characters and include upper and lowercase letters - plus numbers OR special characters.": "\u5bc6\u7801\u5fc5\u987b\u81f3\u5c11\u5305\u542b 8 \u4e2a\u5b57\u7b26\uff0c\u5e76\u4e14\u5305\u542b\u5927\u5199\u548c\u5c0f\u5199\u5b57\u6bcd\u4ee5\u53ca\u6570\u5b57\u6216\u7279\u6b8a\u5b57\u7b26\u3002",
    "Name": "\u540d\u79f0",
    "No App Display Name!": "\u65e0\u5e94\u7528\u7a0b\u5e8f\u663e\u793a\u540d\u79f0\uff01",
    "No Company Display Name!": "\u65e0\u516c\u53f8\u663e\u793a\u540d\u79f0\uff01",
    "No file Selected": "\u672a\u9009\u62e9\u6587\u4ef6",
    "No. of Courses": "\u8bfe\u7a0b\u6570\u91cf",
    "No. of Participants": "\u53c2\u4e0e\u8005\u4eba\u6570",
    "NoName": "NoName",
    "None": "\u65e0",
    "Notification": "\u901a\u77e5",
    "Observer": "\u89c2\u5bdf\u5458",
    "Only alphanumeric characters and spaces allowed": "\u4ec5\u5141\u8bb8\u5b57\u6bcd\u6570\u5b57\u5b57\u7b26\u548c\u7a7a\u683c",
    "Participant": "\u53c2\u4e0e\u8005",
    "Participants": "\u53c2\u4e0e\u8005",
    "Please enter new template name!": "\u8bf7\u8f93\u5165\u65b0\u6a21\u677f\u540d\u79f0\uff01",
    "Please enter preview email!": "\u8bf7\u8f93\u5165\u9884\u89c8\u7535\u5b50\u90ae\u4ef6\uff01",
    "Please enter updated template name or leave the old one!": "\u8bf7\u8f93\u5165\u66f4\u65b0\u7684\u6a21\u677f\u540d\u79f0\u6216\u4fdd\u7559\u65e7\u7684\u6a21\u677f\u540d\u79f0\uff01",
    "Please select at least one course": "\u8bf7\u81f3\u5c11\u9009\u62e9\u4e00\u95e8\u8bfe\u7a0b",
    "Please select at least one student": "\u8bf7\u81f3\u5c11\u9009\u62e9\u4e00\u540d\u5b66\u5458",
    "Please select file first.": "\u8bf7\u5148\u9009\u62e9\u6587\u4ef6\u3002",
    "Please select file for upload.": "\u8bf7\u9009\u62e9\u8981\u4e0a\u4f20\u7684\u6587\u4ef6\u3002",
    "Please select project": "\u8bf7\u9009\u62e9\u9879\u76ee",
    "Poll/Survey Question": "\u6295\u7968/\u8c03\u67e5\u95ee\u5377",
    "Preview Email!": "\u9884\u89c8\u7535\u5b50\u90ae\u4ef6\uff01",
    "Proficiency": "\u719f\u7ec3\u7a0b\u5ea6",
    "Program": "\u8ba1\u5212",
    "Progress": "\u8fdb\u5ea6",
    "Progress : 0%": "\u8fdb\u5ea6\uff1a0%",
    "Progress: %(progress)s %": "\u8fdb\u5ea6\uff1a%(progress)s% ",
    "Progress: %(value)s%": "\u8fdb\u5ea6\uff1a%(value)s%",
    "Report of bulk update will be sent to your email.": "\u6279\u91cf\u66f4\u65b0\u62a5\u544a\u5c06\u53d1\u9001\u5230\u60a8\u7684\u7535\u5b50\u90ae\u7bb1\u3002",
    "Request Time": "\u8bf7\u6c42\u65f6\u95f4",
    "Save Changes": "\u4fdd\u5b58\u66f4\u6539",
    "Search by Keyword": "\u6309\u5173\u952e\u5b57\u641c\u7d22",
    "Select Course": "\u9009\u62e9\u8bfe\u7a0b",
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "\u5df2\u9009\u62e9\uff1a%(selected)s\uff0c\u6210\u529f\uff1a%(successful)s\uff0c\u5931\u8d25\uff1a%(failed)s",
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "\u5df2\u9009\u62e9\uff1a%(selectedRows)s\uff0c\u6210\u529f\uff1a0\uff0c\u5931\u8d25\uff1a0 ",
    "Send": "\u53d1\u9001",
    "Send Course Intro Email": "\u53d1\u9001\u8bfe\u7a0b\u4ecb\u7ecd\u7535\u5b50\u90ae\u4ef6",
    "Show Errors": "\u663e\u793a\u9519\u8bef",
    "Show password": "\u663e\u793a\u5bc6\u7801",
    "Start": "\u5f00\u59cb",
    "Start time": "\u5f00\u59cb\u65f6\u95f4",
    "Status": "\u72b6\u6001",
    "Successful": "\u5bfc\u5165\u6210\u529f",
    "Successfully Enrolled in 1 Course": "\u5df2\u6210\u529f\u6ce8\u518c 1 \u95e8\u8bfe\u7a0b",
    "Successfully added new template!": "\u65b0\u6a21\u677f\u6dfb\u52a0\u6210\u529f\uff01",
    "Successfully deleted template!": "\u6a21\u677f\u5220\u9664\u6210\u529f\uff01",
    "Successfully sent email!": "\u7535\u5b50\u90ae\u4ef6\u53d1\u9001\u6210\u529f\uff01",
    "Successfully sent preview email!": "\u9884\u89c8\u7535\u5b50\u90ae\u4ef6\u53d1\u9001\u6210\u529f\uff01",
    "Successfully updated template!": "\u6a21\u677f\u66f4\u65b0\u6210\u529f\uff01",
    "TA": "\u52a9\u6559",
    "Task failed to execute. Please retry later.": "\u4efb\u52a1\u672a\u80fd\u6267\u884c\u3002\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002",
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "\u8be5 .csv \u6587\u4ef6\u884c\u6570\u4e3a %(lines)s\uff0c\u8d85\u51fa %(limit)s \u884c\u9650\u5236\uff0c\u8bf7\u5c06\u5176\u5206\u5272\u4e3a\u591a\u4e2a\u6587\u4ef6\uff01",
    "The content takes place in a new window.": "\u5185\u5bb9\u51fa\u73b0\u5728\u65b0\u7a97\u53e3\u4e2d\u3002",
    "There was an error submitting your file.": "\u63d0\u4ea4\u6587\u4ef6\u65f6\u51fa\u9519\u3002",
    "This app name cannot contain non-alphanumeric characters!": "\u6b64\u5e94\u7528\u7a0b\u5e8f\u540d\u79f0\u4e0d\u5f97\u5305\u542b\u975e\u5b57\u6bcd\u6570\u5b57\u5b57\u7b26\uff01",
    "This app name cannot have more than 30 characters!": "\u6b64\u5e94\u7528\u7a0b\u5e8f\u540d\u79f0\u4e0d\u5f97\u8d85\u8fc7 30 \u4e2a\u5b57\u7b26\uff01",
    "This company name cannot contain non-alphanumeric characters!": "\u516c\u53f8\u540d\u79f0\u4e0d\u80fd\u5305\u542b\u975e\u5b57\u6bcd\u6570\u5b57\u5b57\u7b26\uff01",
    "This company name cannot have more than 30 characters!": "\u516c\u53f8\u540d\u79f0\u4e0d\u5f97\u8d85\u8fc7 30 \u4e2a\u5b57\u7b26\uff01",
    "This field is required.": "\u6b64\u5b57\u6bb5\u4e3a\u5fc5\u586b\u3002",
    "This tag name cannot contain non-alphanumeric characters!": "\u6b64\u6807\u7b7e\u540d\u79f0\u4e0d\u5f97\u5305\u542b\u975e\u5b57\u6bcd\u6570\u5b57\u5b57\u7b26\uff01",
    "This tag name cannot have more than 30 characters!": "\u6b64\u6807\u7b7e\u540d\u79f0\u4e0d\u5f97\u8d85\u8fc7 30 \u4e2a\u5b57\u7b26\uff01",
    "Today at ": "\u4eca\u5929",
    "Try selecting your company from the type-ahead results.": "\u5c1d\u8bd5\u4ece\u9884\u8f93\u5165\u7ed3\u679c\u4e2d\u9009\u62e9\u60a8\u7684\u516c\u53f8\u3002",
    "Unenroll": "\u53d6\u6d88\u6ce8\u518c",
    "Unenroll Participants": "\u53d6\u6d88\u6ce8\u518c\u7684\u53c2\u4e0e\u8005",
    "Unenroll all selected participants from this course?": "\u53d6\u6d88\u6ce8\u518c\u672c\u8bfe\u7a0b\u7684\u6240\u6709\u9009\u5b9a\u53c2\u4e0e\u8005\uff1f",
    "Updated user data!": "\u7528\u6237\u6570\u636e\u5df2\u66f4\u65b0\uff01",
    "Urban Airship URL": "Urban Airship URL",
    "User successfully enrolled in course": "\u7528\u6237\u5df2\u6210\u529f\u6ce8\u518c\u8bfe\u7a0b",
    "User will be enrolled in course selected below.": "\u5c06\u4e3a\u7528\u6237\u6ce8\u518c\u4e0b\u65b9\u9009\u5b9a\u7684\u8bfe\u7a0b\u3002",
    "Username": "\u7528\u6237\u540d",
    "Username can't be empty! ": "\u7528\u6237\u540d\u4e0d\u80fd\u4e3a\u7a7a\uff01",
    "View Details": "\u67e5\u770b\u8be6\u7ec6\u4fe1\u606f",
    "We'll e-mail you when your report is ready to download.": "\u5f53\u62a5\u544a\u51c6\u5907\u5c31\u7eea\u53ef\u4f9b\u4e0b\u8f7d\u65f6\uff0c\u6211\u4eec\u4f1a\u901a\u8fc7\u90ae\u4ef6\u901a\u77e5\u60a8\u3002",
    "Webinar": "\u7f51\u7edc\u7814\u8ba8\u4f1a",
    "Welcome to McKinsey Academy": "\u6b22\u8fce\u6765\u5230\u9ea6\u80af\u9521\u5b66\u9662",
    "What would you like to do now?": "\u60a8\u73b0\u5728\u60f3\u8981\u505a\u4ec0\u4e48\uff1f",
    "You are about to delete email template. Are you sure?": "\u60a8\u5373\u5c06\u5220\u9664\u7535\u5b50\u90ae\u4ef6\u6a21\u677f\u3002\u786e\u5b9a\uff1f",
    "You are now": "\u60a8\u76ee\u524d\u5728",
    "You can only add up to 4 fields": "\u60a8\u6700\u591a\u53ef\u6dfb\u52a0 4 \u4e2a\u5b57\u6bb5",
    "You don't have permission to create a new tag, please select one from the list!": "\u60a8\u65e0\u6743\u521b\u5efa\u65b0\u6807\u7b7e\uff0c\u8bf7\u4ece\u5217\u8868\u4e2d\u9009\u62e9\u4e00\u4e2a\u6807\u7b7e\uff01",
    "You need to enter course ID!": "\u60a8\u9700\u8981\u8f93\u5165\u8bfe\u7a0b ID\uff01",
    "You need to enter name!": "\u60a8\u9700\u8981\u8f93\u5165\u540d\u5b57\uff01",
    "You need to select at least one participant to be able to apply bulk actions.": "\u8981\u5e94\u7528\u6279\u91cf\u64cd\u4f5c\uff0c\u60a8\u5fc5\u987b\u81f3\u5c11\u9009\u62e9\u4e00\u540d\u53c2\u4e0e\u8005\u3002",
    "You need to select course!": "\u60a8\u9700\u8981\u9009\u62e9\u8bfe\u7a0b\uff01",
    "You need to select status!": "\u60a8\u9700\u8981\u9009\u62e9\u72b6\u6001\uff01",
    "You were logged out due to inactivity. Please log back in to continue.": "\u957f\u65f6\u95f4\u65e0\u64cd\u4f5c\u767b\u51fa\u3002\u8bf7\u91cd\u65b0\u767b\u5f55\u3002",
    "Your Progress: %(value)s%": "\u60a8\u7684\u8fdb\u5ea6\uff1a%(value)s%",
    "Your course begins in %(days)s day.": [
      "\u60a8\u7684\u8bfe\u7a0b\u4e8e %(days)s \u5929\u540e\u5f00\u59cb\u3002",
      "\u60a8\u7684\u8bfe\u7a0b\u4e8e %(days)s \u5929\u540e\u5f00\u59cb\u3002",
      "\u60a8\u7684\u8bfe\u7a0b\u4e8e %(days)s \u5929\u540e\u5f00\u59cb\u3002",
      "\u60a8\u7684\u8bfe\u7a0b\u4e8e %(days)s \u5929\u540e\u5f00\u59cb\u3002",
      "\u60a8\u7684\u8bfe\u7a0b\u4e8e %(days)s \u5929\u540e\u5f00\u59cb\u3002",
      "\u60a8\u7684\u8bfe\u7a0b\u4e8e %(days)s \u5929\u540e\u5f00\u59cb\u3002"
    ],
    "Your course hasn't begun yet. ": "\u60a8\u7684\u8bfe\u7a0b\u5c1a\u672a\u5f00\u59cb\u3002",
    "complete": "\u5b8c\u6210",
    "contains %s learner": [
      "\u5305\u542b%s \u4e2a\u5b66\u5458",
      "\u5305\u542b%s \u4e2a\u5b66\u5458",
      "\u5305\u542b%s \u4e2a\u5b66\u5458",
      "\u5305\u542b%s \u4e2a\u5b66\u5458",
      "\u5305\u542b%s \u4e2a\u5b66\u5458",
      "\u5305\u542b%s \u4e2a\u5b66\u5458"
    ],
    "course id": "\u8bfe\u7a0b ID",
    "email": "\u7535\u5b50\u90ae\u4ef6",
    "for": "\u5bf9\u4e8e",
    "iOS DL URL": "iOS \u4e0b\u8f7d URL",
    "in the cohort!": "\u5728\u5c0f\u7ec4\u4e2d !",
    "location": "\u6240\u5728\u5730",
    "same as your organization's average": "\u7b49\u4e8e\u7ec4\u7ec7\u5e73\u5747\u503c",
    "status": "\u72b6\u6001"
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
    "DATETIME_FORMAT": "N j, Y, P",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%Y",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M",
      "%m/%d/%y"
    ],
    "DATE_FORMAT": "N j, Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%b %d %Y",
      "%b %d, %Y",
      "%d %b %Y",
      "%d %b, %Y",
      "%B %d %Y",
      "%B %d, %Y",
      "%d %B %Y",
      "%d %B, %Y"
    ],
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "F j",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "m/d/Y P",
    "SHORT_DATE_FORMAT": "%m/%d/%Y",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "P",
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

