

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
    " day": " \u65e5", 
    " week": " \u9031", 
    "# of people": "\u4eba\u6570", 
    "% total cohort": "%\u5408\u8a08\u30b3\u30db\u30fc\u30c8", 
    "%(count)s Course Tagged with %(tagDetails)s": [
      "%(count)s\u306e\u30b3\u30fc\u30b9\u304c%(tagDetails)s\u3068\u30bf\u30b0\u4ed8\u3051\u3055\u308c\u307e\u3057\u305f", 
      "%(count)s\u306e\u30b3\u30fc\u30b9\u304c%(tagDetails)s\u3068\u30bf\u30b0\u4ed8\u3051\u3055\u308c\u307e\u3057\u305f"
    ], 
    "%(courseStr)s Before the course begins, you can explore this site to learn more about what to expect.": "%(courseStr)s \u30b3\u30fc\u30b9\u304c\u59cb\u307e\u308b\u307e\u3067\u306f\u3001\u30b5\u30a4\u30c8\u5185\u306e\u5404\u30da\u30fc\u30b8\u306e\u60c5\u5831\u304b\u3089\u63d0\u4f9b\u5185\u5bb9\u3092\u3054\u78ba\u8a8d\u304f\u3060\u3055\u3044\u3002", 
    "%(sel)s of %(cnt)s selected": [
      "%(cnt)s\u500b\u4e2d%(sel)s\u500b\u9078\u629e"
    ], 
    "%(selectedRows)s Participants will be enroll in course selected below.": [
      "%(selectedRows)s\u4eba\u306e\u53c2\u52a0\u8005\u304c\u4e0b\u8a18\u306e\u9078\u629e\u3055\u308c\u305f\u30b3\u30fc\u30b9\u306b\u767b\u9332\u3055\u308c\u307e\u3059\u3002", 
      "%(selectedRows)s\u4eba\u306e\u53c2\u52a0\u8005\u304c\u4e0b\u8a18\u306e\u9078\u629e\u3055\u308c\u305f\u30b3\u30fc\u30b9\u306b\u767b\u9332\u3055\u308c\u307e\u3059\u3002"
    ], 
    "%(value)s%": "%(value)s%", 
    "%s invalid email was ignored.": [
      "%s\u7121\u52b9\u306aE\u30e1\u30fc\u30eb\u306f\u7121\u8996\u3055\u308c\u307e\u3057\u305f\u3002", 
      "%s\u7121\u52b9\u306aE\u30e1\u30fc\u30eb\u306f\u7121\u8996\u3055\u308c\u307e\u3057\u305f\u3002"
    ], 
    "%s learner has been added to this cohort.": [
      "%s\u5b66\u7fd2\u8005\u304c\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u8ffd\u52a0\u3055\u308c\u307e\u3057\u305f\u3002", 
      "%s\u5b66\u7fd2\u8005\u304c\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u8ffd\u52a0\u3055\u308c\u307e\u3057\u305f\u3002"
    ], 
    "%s learner has been moved to this cohort.": [
      "%s\u5b66\u7fd2\u8005\u304c\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u79fb\u52d5\u3055\u308c\u307e\u3057\u305f\u3002", 
      "%s\u5b66\u7fd2\u8005\u304c\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u79fb\u52d5\u3055\u308c\u307e\u3057\u305f\u3002"
    ], 
    "%s learner was preassigned to this cohort. This learner will automatically be added to the cohort when they enroll in the course.": [
      "%s\u5b66\u7fd2\u8005\u304c\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u4e8b\u524d\u306b\u5272\u308a\u5f53\u3066\u3089\u308c\u307e\u3057\u305f\u3002\u3053\u306e\u5b66\u7fd2\u8005\u306f\u30b3\u30fc\u30b9\u306b\u767b\u9332\u3057\u305f\u969b\u306b\u81ea\u52d5\u7684\u306b\u30b3\u30db\u30fc\u30c8\u306b\u8ffd\u52a0\u3055\u308c\u307e\u3059\u3002", 
      "%s\u5b66\u7fd2\u8005\u304c\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u4e8b\u524d\u306b\u5272\u308a\u5f53\u3066\u3089\u308c\u307e\u3057\u305f\u3002\u3053\u308c\u3089\u306e\u5b66\u7fd2\u8005\u306f\u30b3\u30fc\u30b9\u306b\u767b\u9332\u3057\u305f\u969b\u306b\u81ea\u52d5\u7684\u306b\u30b3\u30db\u30fc\u30c8\u306b\u8ffd\u52a0\u3055\u308c\u307e\u3059\u3002"
    ], 
    "%s user was already in this cohort.": [
      "%s\u30e6\u30fc\u30b6\u30fc\u306f\u65e2\u306b\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u3044\u307e\u3057\u305f\u3002", 
      "%s\u30e6\u30fc\u30b6\u30fc\u306f\u65e2\u306b\u3053\u306e\u30b3\u30db\u30fc\u30c8\u306b\u3044\u307e\u3057\u305f\u3002"
    ], 
    "%s user/email was not found.": [
      "%s\u30e6\u30fc\u30b6\u30fc/E\u30e1\u30fc\u30eb\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3067\u3057\u305f\u3002", 
      "%s\u30e6\u30fc\u30b6\u30fc/E\u30e1\u30fc\u30eb\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3067\u3057\u305f\u3002"
    ], 
    ".0%": ".0%", 
    "2 or more fields can not have the same name": "2\u3064\u4ee5\u4e0a\u306e\u6b04\u306b\u540c\u3058\u540d\u524d\u3092\u5165\u529b\u3059\u308b\u3053\u3068\u306f\u3067\u304d\u307e\u305b\u3093\u3002", 
    "6 a.m.": "\u5348\u524d 6 \u6642", 
    "6 p.m.": "\u5348\u5f8c 6 \u6642", 
    "<span class=\"green\"> %(diff)s point</span> above your organization's average": [
      "\u7d44\u7e54\u306e\u5e73\u5747\u306e<span class=\"green\">%(diff)s\u30dd\u30a4\u30f3\u30c8</span>\u4ee5\u4e0a", 
      "\u7d44\u7e54\u306e\u5e73\u5747\u306e<span class=\"green\">%(diff)s\u30dd\u30a4\u30f3\u30c8</span>\u4ee5\u4e0a"
    ], 
    "<span class=\"green\">%(diff)s% </span> above your organization's average": "\u7d44\u7e54\u306e\u5e73\u5747\u306e<span class=\"green\">%(diff)s% </span>\u4ee5\u4e0a", 
    "<span class=\"red\"> %(diff)s point</span> below your organization's average": [
      "\u7d44\u7e54\u306e\u5e73\u5747\u306e<span class=\"red\"> %(diff)s\u30dd\u30a4\u30f3\u30c8</span>\u4ee5\u4e0b", 
      "\u7d44\u7e54\u306e\u5e73\u5747\u306e<span class=\"red\"> %(diff)s\u30dd\u30a4\u30f3\u30c8</span>\u4ee5\u4e0b"
    ], 
    "<span class=\"red\"> %(diff)s% </span> below your organization's average": "\u7d44\u7e54\u306e\u5e73\u5747\u306e<span class=\"red\"> %(diff)s% </span>\u4ee5\u4e0b", 
    "Activated": "\u6709\u52b9\u5316\u6e08\u307f", 
    "Activation Link": "\u6709\u52b9\u5316\u30ea\u30f3\u30af", 
    "Active": "\u6709\u52b9", 
    "Add new role e.g CEO,CTO": "\u65b0\u898f\u306e\u30ed\u30fc\u30eb (CEO\u3001CTO\u306a\u3069) \u3092\u8ffd\u52a0\u3059\u308b", 
    "Admin Company": "\u7ba1\u7406\u4f1a\u793e", 
    "Admin Permissions": "\u7ba1\u7406\u8005\u306e\u8a31\u53ef", 
    "All students added to private group have to be members of same company.": "\u30d7\u30e9\u30a4\u30d9\u30fc\u30c8\u30b0\u30eb\u30fc\u30d7\u306b\u8ffd\u52a0\u3055\u308c\u308b\u751f\u5f92\u306f\u5168\u54e1\u3001\u540c\u3058\u4f1a\u793e\u306e\u793e\u54e1\u3067\u3042\u308b\u5fc5\u8981\u304c\u3042\u308a\u307e\u3059\u3002", 
    "An error occurred submitting the request.": "\u30ea\u30af\u30a8\u30b9\u30c8\u306e\u9001\u4fe1\u6ce8\u306b\u30a8\u30e9\u30fc\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002", 
    "Analytics URL": "Analytics URL", 
    "Android DL URL": "Android DL URL", 
    "Announcements": "\u304a\u77e5\u3089\u305b", 
    "App Name": "\u30a2\u30d7\u30ea\u540d", 
    "April": "4\u6708", 
    "Are you sure you want to remove this ?": "\u672c\u5f53\u306b\u3053\u308c\u3092\u6d88\u53bb\u3057\u307e\u3059\u304b?", 
    "Are you sure you want to remove this group? Doing so will remove submissions and feedback associated with the group.": "\u672c\u5f53\u306b\u3053\u306e\u30b0\u30eb\u30fc\u30d7\u3092\u524a\u9664\u3057\u3066\u3088\u308d\u3057\u3044\u3067\u3059\u304b? \u305d\u308c\u306b\u3088\u308a\u3001\u3053\u306e\u30b0\u30eb\u30fc\u30d7\u306b\u95a2\u4fc2\u3059\u308b\u63d0\u51fa\u7269\u304a\u3088\u3073\u30d5\u30a3\u30fc\u30c9\u30d0\u30c3\u30af\u304c\u524a\u9664\u3055\u308c\u307e\u3059\u3002", 
    "Are you sure?": "\u672c\u5f53\u306b\u3088\u308d\u3057\u3044\u3067\u3059\u304b?", 
    "Assessment: %(label)s": "\u8a55\u4fa1: %(label)s", 
    "August": "8\u6708", 
    "Available %s": "\u5229\u7528\u53ef\u80fd %s", 
    "Avg Progress": "\u5e73\u5747\u9032\u5ea6", 
    "Business Function": "\u4e8b\u696d\u6a5f\u80fd", 
    "Business Unit": "\u4e8b\u696d\u90e8\u9580", 
    "Cancel": "\u30ad\u30e3\u30f3\u30bb\u30eb", 
    "Change Status": "\u30b9\u30c6\u30fc\u30bf\u30b9\u3092\u5909\u66f4\u3059\u308b", 
    "Change status of all selected participants to:": "\u3059\u3079\u3066\u306e\u9078\u629e\u3057\u305f\u53c2\u52a0\u8005\u3092\u6b21\u306e\u30b9\u30c6\u30fc\u30bf\u30b9\u306b\u5909\u66f4\u3059\u308b:", 
    "Check for Completion": "\u5b8c\u4e86\u3057\u305f\u3053\u3068\u3092\u78ba\u8a8d\u3057\u307e\u3059", 
    "Choose": "\u9078\u629e", 
    "Choose a Date": "\u65e5\u4ed8\u3092\u9078\u629e", 
    "Choose a Time": "\u6642\u9593\u3092\u9078\u629e", 
    "Choose a time": "\u6642\u9593\u3092\u9078\u629e", 
    "Choose all": "\u5168\u3066\u9078\u629e", 
    "Chosen %s": "\u9078\u629e\u3055\u308c\u305f %s", 
    "Click Add to specify Lesson Label": "[\u8ffd\u52a0]\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u30ec\u30c3\u30b9\u30f3\u30e9\u30d9\u30eb\u3092\u6307\u5b9a\u3057\u307e\u3059", 
    "Click Add to specify Lessons Label": "[\u8ffd\u52a0]\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u30ec\u30c3\u30b9\u30f3\u30e9\u30d9\u30eb\u3092\u6307\u5b9a\u3057\u307e\u3059", 
    "Click Add to specify Module Label": "[\u8ffd\u52a0]\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u30e2\u30b8\u30e5\u30fc\u30eb\u30e9\u30d9\u30eb\u3092\u6307\u5b9a\u3057\u307e\u3059", 
    "Click Add to specify Modules Label": "[\u8ffd\u52a0]\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u30e2\u30b8\u30e5\u30fc\u30eb\u30e9\u30d9\u30eb\u3092\u6307\u5b9a\u3057\u307e\u3059", 
    "Click to choose all %s at once.": "\u30af\u30ea\u30c3\u30af\u3059\u308b\u3068\u3059\u3079\u3066\u306e %s \u3092\u9078\u629e\u3057\u307e\u3059\u3002", 
    "Click to remove all chosen %s at once.": "\u30af\u30ea\u30c3\u30af\u3059\u308b\u3068\u3059\u3079\u3066\u306e %s \u3092\u9078\u629e\u304b\u3089\u524a\u9664\u3057\u307e\u3059\u3002", 
    "Cohort Comp.": "\u30b3\u30db\u30fc\u30c8\u4f1a\u793e", 
    "Company": "\u4f1a\u793e", 
    "Company Admin": "\u4f1a\u793e\u306e\u7ba1\u7406\u8005", 
    "Company ID": "\u4f1a\u793eID", 
    "Company doesn't exist! ": "\u4f1a\u793e\u306f\u5b58\u5728\u3057\u307e\u305b\u3093\u3002", 
    "Complete": "\u5b8c\u4e86", 
    "Complete all content to continue": "\u7d9a\u884c\u3059\u308b\u306b\u306f\u3059\u3079\u3066\u306e\u5185\u5bb9\u3092\u5b8c\u4e86\u3057\u3066\u304f\u3060\u3055\u3044", 
    "Complete all content to continue.": "\u7d9a\u884c\u3059\u308b\u306b\u306f\u3059\u3079\u3066\u306e\u5185\u5bb9\u3092\u5b8c\u4e86\u3057\u3066\u304f\u3060\u3055\u3044", 
    "Completed": "\u5b8c\u4e86", 
    "Content is complete, please continue.": "\u5185\u5bb9\u304c\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002\u7d9a\u884c\u3057\u3066\u304f\u3060\u3055\u3044", 
    "Couldn't add tag to course!": "\u30b3\u30fc\u30b9\u306b\u30bf\u30b0\u304c\u8ffd\u52a0\u3067\u304d\u307e\u305b\u3093\u3002", 
    "Couldn't create new company!": "\u65b0\u3057\u3044\u4f1a\u793e\u3092\u4f5c\u6210\u3067\u304d\u307e\u305b\u3093\u3067\u3057\u305f\u3002", 
    "Couldn't create new tag!": "\u65b0\u3057\u3044\u30bf\u30b0\u3092\u4f5c\u6210\u3067\u304d\u307e\u305b\u3093\u3067\u3057\u305f\u3002", 
    "Couldn't delete tag!": "\u30bf\u30b0\u3092\u524a\u9664\u3067\u304d\u307e\u305b\u3093\u3067\u3057\u305f\u3002", 
    "Couldn't delink App!": "\u30a2\u30d7\u30ea\u3078\u306e\u30ea\u30f3\u30af\u3092\u524a\u9664\u3067\u304d\u307e\u305b\u3093\u3002", 
    "Couldn't link this App!": "\u3053\u306e\u30a2\u30d7\u30ea\u3092\u30ea\u30f3\u30af\u3067\u304d\u307e\u305b\u3093\u3002", 
    "Country": "\u56fd", 
    "Course": "\u30b3\u30fc\u30b9", 
    "Course ID": "\u30b3\u30fc\u30b9ID", 
    "Course Name": "\u30b3\u30fc\u30b9\u540d", 
    "Dashboard Name": "\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9\u540d", 
    "Date Added": "\u30c7\u30fc\u30bf\u304c\u8ffd\u52a0\u3055\u308c\u307e\u3057\u305f", 
    "December": "12\u6708", 
    "Delete Role": "\u30ed\u30fc\u30eb\u3092\u524a\u9664\u3059\u308b", 
    "Deployment Mech": "\u958b\u767a\u30e1\u30ab\u30cb\u30ba\u30e0", 
    "Digital Content": "\u30c7\u30b8\u30bf\u30eb\u30b3\u30f3\u30c6\u30f3\u30c4", 
    "Digital Course": "\u30c7\u30b8\u30bf\u30eb\u30b3\u30fc\u30b9", 
    "Discussion": "\u691c\u8a0e\u4e8b\u9805", 
    "Do you really want to delete: \n": "\u672c\u5f53\u306b\u6d88\u53bb\u3057\u307e\u3059\u304b: \n", 
    "Download": "\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9", 
    "Download CSV File": "CSV\u30d5\u30a1\u30a4\u30eb\u3092\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9\u3059\u308b", 
    "Download Notifications CSV": "\u901a\u77e5CSV\u3092\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9\u3059\u308b", 
    "Email": "E\u30e1\u30fc\u30eb", 
    "Email Preview Success!": "E\u30e1\u30fc\u30eb\u30d7\u30ec\u30d3\u30e5\u30fc\u3092\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "Email Success!": "E\u30e1\u30fc\u30eb\u5b8c\u4e86\u3002", 
    "Email can't be empty! ": "E\u30e1\u30fc\u30eb\u306f\u5fc5\u305a\u8a18\u5165\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "End": "\u7d42\u4e86", 
    "End Date": "\u7d42\u4e86\u65e5", 
    "Engagement": "\u30a8\u30f3\u30b2\u30fc\u30b8\u30e1\u30f3\u30c8", 
    "Enroll Participant": "\u53c2\u52a0\u8005\u3092\u767b\u9332\u3059\u308b", 
    "Enroll Participants": "\u53c2\u52a0\u8005\u3092\u767b\u9332\u3059\u308b", 
    "Enroll this list in another course": "\u4ed6\u306e\u30b3\u30fc\u30b9\u306b\u3053\u306e\u4e00\u89a7\u3092\u767b\u9332\u3059\u308b", 
    "Enrolled In": "\u767b\u9332\u6e08\u307f", 
    "Error File": "\u30a8\u30e9\u30fc\u30d5\u30a1\u30a4\u30eb", 
    "Error Occured!": "\u30a8\u30e9\u30fc\u304c\u767a\u751f\u3057\u307e\u3044\u305f\uff01", 
    "Error initiating the report generation. Please retry later.": "\u30ec\u30dd\u30fc\u30c8\u4f5c\u6210\u958b\u59cb\u30a8\u30e9\u30fc\u3002\u5f8c\u3067\u3084\u308a\u76f4\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Error processing CSV file.": "CSV\u30d5\u30a1\u30a4\u30eb\u306e\u51e6\u7406\u3067\u30a8\u30e9\u30fc\u3002", 
    "Error uploading file. Please try again and be sure to use an accepted file format.": "\u30d5\u30a1\u30a4\u30eb\u306e\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u4e2d\u306b\u30a8\u30e9\u30fc\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002\u4f7f\u7528\u53ef\u80fd\u306a\u30d5\u30a1\u30a4\u30eb\u5f62\u5f0f\u3092\u78ba\u8a8d\u3057\u3001\u518d\u5ea6\u8a66\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Export Report": "\u30ec\u30dd\u30fc\u30c8\u3092\u30a8\u30af\u30b9\u30dd\u30fc\u30c8\u3059\u308b", 
    "Exporting Stats for All Users": "\u3059\u3079\u3066\u306e\u30e6\u30fc\u30b6\u30fc\u306e\u30b9\u30c6\u30a4\u30bf\u30b9\u3092\u30a8\u30af\u30b9\u30dd\u30fc\u30c8\u3059\u308b", 
    "February": "2\u6708", 
    "Female": "\u5973\u6027", 
    "Fetching data for file: %(filename)s": "\u30d5\u30a1\u30a4\u30eb: %(filename)s\u306e\u30c7\u30fc\u30bf\u3092\u53d6\u308a\u8fbc\u307f\u4e2d", 
    "File name": "\u540d\u524d", 
    "File successfully uploaded!": "\u30d5\u30a1\u30a4\u30eb\u306e\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u3092\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "Filter": "\u30d5\u30a3\u30eb\u30bf\u30fc", 
    "First name can't be empty! ": "\u540d\u524d\u306f\u5fc5\u305a\u8a18\u5165\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Go to %(course_id)s Course": "%(course_id)s\u30b3\u30fc\u30b9\u3092\u898b\u308b", 
    "Grade": "\u6210\u7e3e", 
    "Group Work": "\u30b0\u30eb\u30fc\u30d7\u30ef\u30fc\u30af", 
    "Group Work: %(label)s": "\u30b0\u30eb\u30fc\u30d7\u30ef\u30fc\u30af: %(label)s", 
    "Group successfully updated": "\u30b0\u30eb\u30fc\u30d7\u306e\u66f4\u65b0\u304c\u5b8c\u4e86\u3057\u307e\u3057\u305f", 
    "Group was not created": "\u30b0\u30eb\u30fc\u30d7\u306f\u4f5c\u6210\u3055\u308c\u307e\u305b\u3093\u3067\u3057\u305f", 
    "Group work": "\u30b0\u30eb\u30fc\u30d7\u30ef\u30fc\u30af", 
    "Hide": "\u975e\u8868\u793a", 
    "Hide Details": "\u8a73\u7d30\u3092\u975e\u8868\u793a", 
    "Hide password": "\u30d1\u30b9\u30ef\u30fc\u30c9\u3092\u975e\u8868\u793a\u306b\u3059\u308b", 
    "I'm Done": "\u7d42\u308f\u308a\u307e\u3057\u305f", 
    "Importing %(processed)s of %(total)s rows": "%(total)s\u5217\u306e%(processed)s\u3092\u30a4\u30f3\u30dd\u30fc\u30c8\u4e2d", 
    "Importing..": "\u30a4\u30f3\u30dd\u30fc\u30c8\u4e2d\u2026", 
    "In Person Session": "\u5bfe\u9762\u30bb\u30c3\u30b7\u30e7\u30f3", 
    "Include breakdown of progress for each lesson (Note: the export will take more time)": "\u30ec\u30c3\u30b9\u30f3\u3054\u3068\u306e\u9032\u5ea6\u306e\u5185\u8a33\u3092\u542b\u3080 (\u6ce8\u8a18: \u30a8\u30af\u30b9\u30dd\u30fc\u30c8\u306b\u306f\u3055\u3089\u306b\u6642\u9593\u3092\u8981\u3057\u307e\u3059)", 
    "Incomplete": "\u672a\u5b8c\u4e86", 
    "Initiated by": "\u958b\u59cb\u8005", 
    "Invalid format for CSV file.": "CSV\u30d5\u30a1\u30a4\u30eb\u306e\u5f62\u5f0f\u304c\u7121\u52b9\u3067\u3059\u3002", 
    "It looks like you're not active. Click OK to keep working.": "\u30a2\u30af\u30c6\u30a3\u30d6\u3067\u306f\u306a\u3044\u3088\u3046\u3067\u3059\u3002[OK]\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u6d3b\u52d5\u3092\u7d9a\u3051\u3066\u304f\u3060\u3055\u3044\u3002", 
    "It looks like your browser settings has pop-ups disabled.": "\u30d6\u30e9\u30a6\u30b6\u30fc\u306e\u8a2d\u5b9a\u3067\u30dd\u30c3\u30d7\u30a2\u30c3\u30d7\u304c\u7121\u52b9\u306b\u306a\u3063\u3066\u3044\u307e\u3059\u3002", 
    "January": "1\u6708", 
    "July": "7\u6708", 
    "June": "6\u6708", 
    "Last Log In": "\u6700\u7d42\u30ed\u30b0\u30a4\u30f3", 
    "Last name can't be empty! ": "\u82d7\u5b57\u306f\u5fc5\u305a\u8a18\u5165\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Launch pop-up to continue": "\u30dd\u30c3\u30d7\u30a2\u30c3\u30d7\u3092\u8d77\u52d5\u3057\u3066\u7d9a\u884c\u3059\u308b", 
    "Leaderboards": "\u30b9\u30b3\u30a2\u30dc\u30fc\u30c9", 
    "Learner email": "\u5b66\u7fd2\u8005E\u30e1\u30fc\u30eb", 
    "Lesson": "\u30ec\u30c3\u30b9\u30f3", 
    "Male": "\u7537\u6027", 
    "Manager email": "\u30de\u30cd\u30fc\u30b8\u30e3\u30fcE\u30e1\u30fc\u30eb", 
    "March": "3\u6708", 
    "May": "5\u6708", 
    "Midnight": "0\u6642", 
    "Moderator": "\u4e3b\u5bb0\u8005", 
    "Module": "\u30e2\u30b8\u30e5\u30fc\u30eb", 
    "Name": "\u540d\u524d", 
    "No App Display Name!": "\u30a2\u30d7\u30ea\u8868\u793a\u540d\u304c\u3042\u308a\u307e\u305b\u3093\u3002", 
    "No Company Display Name!": "\u4f1a\u793e\u8868\u793a\u540d\u304c\u3042\u308a\u307e\u305b\u3093\u3002", 
    "No file Selected": "\u30d5\u30a1\u30a4\u30eb\u304c\u9078\u629e\u3055\u308c\u3066\u3044\u307e\u305b\u3093\u3002", 
    "No. of Courses": "\u30b3\u30fc\u30b9\u6570:", 
    "No. of Participants": "\u53c2\u52a0\u8005\u6570", 
    "NoName": "\u7121\u540d", 
    "None": "\u306a\u3057", 
    "Noon": "12\u6642", 
    "Note: You are %s hour ahead of server time.": [
      "\u30ce\u30fc\u30c8: \u3042\u306a\u305f\u306e\u74b0\u5883\u306f\u30b5\u30fc\u30d0\u30fc\u6642\u9593\u3088\u308a\u3001%s\u6642\u9593\u9032\u3093\u3067\u3044\u307e\u3059\u3002"
    ], 
    "Note: You are %s hour behind server time.": [
      "\u30ce\u30fc\u30c8: \u3042\u306a\u305f\u306e\u74b0\u5883\u306f\u30b5\u30fc\u30d0\u30fc\u6642\u9593\u3088\u308a\u3001%s\u6642\u9593\u9045\u308c\u3066\u3044\u307e\u3059\u3002"
    ], 
    "Notification": "\u901a\u77e5", 
    "November": "11\u6708", 
    "Now": "\u73fe\u5728", 
    "Observer": "\u76e3\u8996\u8005", 
    "October": "10\u6708", 
    "Only alphanumeric characters and spaces allowed": "\u82f1\u6570\u5b57\u3068\u30b9\u30da\u30fc\u30b9\u3060\u3051\u304c\u8a31\u53ef\u3055\u308c\u3066\u3044\u307e\u3059", 
    "Participant": "\u53c2\u52a0\u8005", 
    "Participants": "\u53c2\u52a0\u8005", 
    "Please enter new template name!": "\u65b0\u3057\u3044\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8\u540d\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Please enter preview email!": "\u30d7\u30ec\u30d3\u30e5\u30fc\u306eE\u30e1\u30fc\u30eb\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Please enter updated template name or leave the old one!": "\u66f4\u65b0\u3057\u305f\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8\u540d\u3092\u5165\u529b\u3059\u308b\u304b\u3001\u53e4\u3044\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8\u540d\u3092\u6b8b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Please select at least one course": "\u30b3\u30fc\u30b9\u3092\u6700\u4f4e1\u500b\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044", 
    "Please select at least one student": "\u751f\u5f92\u3092\u6700\u4f4e1\u540d\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044", 
    "Please select file first.": "\u307e\u305a\u30d5\u30a1\u30a4\u30eb\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Please select file for upload.": "\u30a2\u30c3\u30d7\u30ed\u30fc\u30c9\u3059\u308b\u30d5\u30a1\u30a4\u30eb\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Please select project": "\u30d7\u30ed\u30b8\u30a7\u30af\u30c8\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044", 
    "Poll/Survey Question": "\u6295\u7968\u8abf\u67fb/\u30a2\u30f3\u30b1\u30fc\u30c8\u8abf\u67fb\u306e\u8cea\u554f", 
    "Preview Email!": "E\u30e1\u30fc\u30eb\u3092\u30d7\u30ec\u30d3\u30e5\u30fc\u3059\u308b\u3002", 
    "Proficiency": "\u7fd2\u719f\u5ea6", 
    "Program": "\u30d7\u30ed\u30b0\u30e9\u30e0", 
    "Progress": "\u9032\u5ea6", 
    "Progress : 0%": "\u9032\u5ea6: 0%", 
    "Progress: %(progress)s %": "\u9032\u5ea6: %(progress)s %", 
    "Progress: %(value)s%": "\u9032\u5ea6: %(value)s%", 
    "Remove": "\u524a\u9664", 
    "Remove all": "\u3059\u3079\u3066\u524a\u9664", 
    "Report of bulk update will be sent to your email.": "\u5927\u91cf\u66f4\u65b0\u306e\u30ec\u30dd\u30fc\u30c8\u304cE\u30e1\u30fc\u30eb\u306b\u9001\u4fe1\u3055\u308c\u307e\u3059\u3002", 
    "Request Time": "\u30ea\u30af\u30a8\u30b9\u30c8\u6642\u9593", 
    "Save Changes": "\u5909\u66f4\u3092\u4fdd\u5b58\u3059\u308b", 
    "Search by Keyword": "\u30ad\u30fc\u30ef\u30fc\u30c9\u3067\u691c\u7d22", 
    "Select Course": "\u30b3\u30fc\u30b9\u3092\u9078\u629e\u3059\u308b", 
    "Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s": "\u9078\u629e\u6e08\u307f: %(selected)s\u3001\u5b8c\u4e86: %(successful)s\u3001\u5931\u6557: %(failed)s", 
    "Selected: %(selectedRows)s, Successful: 0, Failed: 0": "\u9078\u629e\u6e08\u307f: %(selectedRows)s\u3001\u5b8c\u4e86: 0\u3001\u5931\u6557: 0", 
    "Send": "\u9001\u4fe1\u3059\u308b", 
    "Send Course Intro Email": "\u30b3\u30fc\u30b9\u7d39\u4ecb\u3092E\u30e1\u30fc\u30eb\u3067\u9001\u4fe1\u3059\u308b", 
    "September": "9\u6708", 
    "Show": "\u8868\u793a", 
    "Show Errors": "\u30a8\u30e9\u30fc\u3092\u8868\u793a\u3059\u308b", 
    "Show password": "\u30d1\u30b9\u30ef\u30fc\u30c9\u3092\u8868\u793a\u3059\u308b", 
    "Start": "\u958b\u59cb", 
    "Status": "\u30b9\u30c6\u30fc\u30bf\u30b9", 
    "Successful": "\u6210\u529f", 
    "Successfully Enrolled in 1 Course": "1\u30b3\u30fc\u30b9\u306b\u7121\u4e8b\u767b\u9332\u304c\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "Successfully added new template!": "\u65b0\u3057\u3044\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8\u306e\u8ffd\u52a0\u3092\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "Successfully deleted template!": "\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8\u306e\u524a\u9664\u3092\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "Successfully sent email!": "\u30e1\u30c3\u30bb\u30fc\u30b8\u306e\u9001\u4fe1\u3092\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "Successfully sent preview email!": "\u30d7\u30ec\u30d3\u30e5\u30fc\u306eE\u30e1\u30fc\u30eb\u306e\u9001\u4fe1\u3092\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "Successfully updated template!": "\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8\u306e\u66f4\u65b0\u3092\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002", 
    "TA": "TA", 
    "Task failed to execute. Please retry later.": "\u30bf\u30b9\u30af\u306e\u5b9f\u884c\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002\u5f8c\u3067\u3084\u308a\u76f4\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!": "\u3053\u306e.csv\u30d5\u30a1\u30a4\u30eb\u306f%(limit)s\u884c: %(lines)s\u4ee5\u4e0a\u3067\u3059\u3002\u30d5\u30a1\u30a4\u30eb\u3092\u5206\u5272\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "The content takes place in a new window.": "\u30b3\u30f3\u30c6\u30f3\u30c4\u306f\u65b0\u3057\u3044\u30a6\u30a3\u30f3\u30c9\u30a6\u3067\u5b9f\u884c\u3055\u308c\u307e\u3059\u3002", 
    "There was an error submitting your file.": "\u30d5\u30a1\u30a4\u30eb\u306e\u9001\u4fe1\u3067\u30a8\u30e9\u30fc\u304c\u767a\u751f\u3057\u307e\u3057\u305f\u3002", 
    "This app name cannot contain non-alphanumeric characters!": "\u30a2\u30d7\u30ea\u540d\u306b\u306f\u82f1\u6570\u5b57\u3057\u304b\u4f7f\u7528\u3067\u304d\u307e\u305b\u3093\u3002", 
    "This app name cannot have more than 30 characters!": "\u30a2\u30d7\u30ea\u540d\u306f30\u6587\u5b57\u4ee5\u4e0b\u306b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "This company name cannot contain non-alphanumeric characters!": "\u4f1a\u793e\u540d\u306b\u306f\u82f1\u6570\u5b57\u3057\u304b\u4f7f\u7528\u3067\u304d\u307e\u305b\u3093\u3002", 
    "This company name cannot have more than 30 characters!": "\u4f1a\u793e\u540d\u306f30\u6587\u5b57\u4ee5\u4e0b\u306b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "\u3053\u308c\u304c\u4f7f\u7528\u53ef\u80fd\u306a %s \u306e\u30ea\u30b9\u30c8\u3067\u3059\u3002\u4e0b\u306e\u30dc\u30c3\u30af\u30b9\u3067\u9805\u76ee\u3092\u9078\u629e\u3057\u30012\u3064\u306e\u30dc\u30c3\u30af\u30b9\u9593\u306e \"\u9078\u629e\"\u306e\u77e2\u5370\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u3001\u3044\u304f\u3064\u304b\u3092\u9078\u629e\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002", 
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "\u3053\u308c\u304c\u9078\u629e\u3055\u308c\u305f %s \u306e\u30ea\u30b9\u30c8\u3067\u3059\u3002\u4e0b\u306e\u30dc\u30c3\u30af\u30b9\u3067\u9078\u629e\u3057\u30012\u3064\u306e\u30dc\u30c3\u30af\u30b9\u9593\u306e \"\u524a\u9664\"\u77e2\u5370\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u4e00\u90e8\u3092\u524a\u9664\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002", 
    "This tag name cannot contain non-alphanumeric characters!": "\u30bf\u30b0\u540d\u306b\u306f\u82f1\u6570\u5b57\u3057\u304b\u4f7f\u7528\u3067\u304d\u307e\u305b\u3093\u3002", 
    "This tag name cannot have more than 30 characters!": "\u30bf\u30b0\u540d\u306f30\u6587\u5b57\u4ee5\u4e0b\u306b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Today": "\u4eca\u65e5", 
    "Today at ": "\u4eca\u65e5", 
    "Tomorrow": "\u660e\u65e5", 
    "Try selecting your company from the type-ahead results.": "\u5148\u884c\u5165\u529b\u7d50\u679c\u304b\u3089\u3042\u306a\u305f\u306e\u4f1a\u793e\u3092\u9078\u629e\u3057\u3066\u307f\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Type into this box to filter down the list of available %s.": "\u4f7f\u7528\u53ef\u80fd\u306a %s \u306e\u30ea\u30b9\u30c8\u3092\u7d5e\u308a\u8fbc\u3080\u306b\u306f\u3001\u3053\u306e\u30dc\u30c3\u30af\u30b9\u306b\u5165\u529b\u3057\u307e\u3059\u3002", 
    "Unenroll": "\u767b\u9332\u89e3\u9664\u3059\u308b", 
    "Unenroll Participants": "\u53c2\u52a0\u8005\u306e\u767b\u9332\u3092\u89e3\u9664\u3059\u308b", 
    "Unenroll all selected participants from this course?": "\u9078\u629e\u3057\u305f\u3059\u3079\u3066\u306e\u53c2\u52a0\u8005\u3092\u3053\u306e\u30b3\u30fc\u30b9\u304b\u3089\u767b\u9332\u89e3\u9664\u3057\u307e\u3059\u304b?", 
    "Updated user data!": "\u30e6\u30fc\u30b6\u30fc\u30c7\u30fc\u30bf\u3092\u66f4\u65b0\u3057\u307e\u3057\u305f\u3002", 
    "Urban Airship URL": "Urban Airship URL", 
    "User successfully enrolled in course": "\u30e6\u30fc\u30b6\u30fc\u306e\u30b3\u30fc\u30b9\u3078\u306e\u767b\u9332\u304c\u5b8c\u4e86\u3057\u307e\u3057\u305f", 
    "User will be enrolled in course selected below.": "\u9078\u629e\u3055\u308c\u305f\u4ee5\u4e0b\u306e\u30b3\u30fc\u30b9\u306b\u30e6\u30fc\u30b6\u30fc\u3092\u767b\u9332\u3057\u307e\u3059\u3002", 
    "Username": "\u30e6\u30fc\u30b6\u30fc\u540d", 
    "Username can't be empty! ": "\u30e6\u30fc\u30b6\u30fc\u30cd\u30fc\u30e0\u306f\u5fc5\u305a\u8a18\u5165\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "View Details": "\u8a73\u7d30\u3092\u8868\u793a", 
    "We'll e-mail you when your report is ready to download.": "\u3042\u306a\u305f\u306e\u30ec\u30dd\u30fc\u30c8\u306e\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9\u306e\u6e96\u5099\u304c\u3067\u304d\u305f\u3068\u304d\u306b\u3001E\u30e1\u30fc\u30eb\u3092\u9001\u4fe1\u3057\u307e\u3059\u3002", 
    "Webinar": "\u30a6\u30a7\u30d3\u30ca\u30fc", 
    "Welcome to McKinsey Academy": "McKinsey Academy\u3078\u3088\u3046\u3053\u305d", 
    "What would you like to do now?": "\u6b21\u306f\u4f55\u3092\u3057\u307e\u3059\u304b?", 
    "Yesterday": "\u6628\u65e5", 
    "You are about to delete email template. Are you sure?": "\u3042\u306a\u305f\u306fE\u30e1\u30fc\u30eb\u30c6\u30f3\u30d7\u30ec\u30fc\u30c8\u3092\u524a\u9664\u3057\u3088\u3046\u3068\u3057\u3066\u3044\u307e\u3059\u3002\u3088\u308d\u3057\u3044\u3067\u3057\u3087\u3046\u304b?", 
    "You are now": "\u3042\u306a\u305f\u306f\u4eca", 
    "You can only add up to 4 fields": "\u6700\u9ad84\u3064\u306e\u6b04\u307e\u3067\u8ffd\u52a0\u3067\u304d\u307e\u3059", 
    "You don't have permission to create a new tag, please select one from the list!": "\u65b0\u3057\u3044\u30bf\u30b0\u3092\u4f5c\u6210\u3059\u308b\u6a29\u9650\u304c\u3042\u308a\u307e\u305b\u3093\u3002\u4e00\u89a7\u304b\u3089\u4e00\u3064\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "\u64cd\u4f5c\u3092\u9078\u629e\u3057\u307e\u3057\u305f\u304c\u3001\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u5909\u66f4\u306f\u3042\u308a\u307e\u305b\u3093\u3067\u3057\u305f\u3002\u3082\u3057\u304b\u3057\u3066\u4fdd\u5b58\u30dc\u30bf\u30f3\u3067\u306f\u306a\u304f\u3066\u5b9f\u884c\u30dc\u30bf\u30f3\u3092\u304a\u63a2\u3057\u3067\u3059\u304b\u3002", 
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "\u64cd\u4f5c\u3092\u9078\u629e\u3057\u307e\u3057\u305f\u304c\u3001\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u304c\u3042\u308a\u307e\u3059\u3002OK\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u4fdd\u5b58\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u305d\u306e\u5f8c\u3001\u64cd\u4f5c\u3092\u518d\u5ea6\u5b9f\u884c\u3059\u308b\u5fc5\u8981\u304c\u3042\u308a\u307e\u3059\u3002", 
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u304c\u3042\u308a\u307e\u3059\u3002\u64cd\u4f5c\u3092\u5b9f\u884c\u3059\u308b\u3068\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u306f\u5931\u308f\u308c\u307e\u3059\u3002", 
    "You need to enter course ID!": "\u30b3\u30fc\u30b9ID\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "You need to enter name!": "\u540d\u524d\u3092\u5165\u529b\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "You need to select at least one participant to be able to apply bulk actions.": "\u4e00\u62ec\u64cd\u4f5c\u3092\u3059\u308b\u306b\u306f\u3001\u6700\u4f4e1\u540d\u306e\u53c2\u52a0\u8005\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "You need to select course!": "\u30b3\u30fc\u30b9\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "You need to select status!": "\u30bf\u30b0\u3092\u9078\u629e\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "You were logged out due to inactivity. Please log back in to continue.": "\u30a2\u30af\u30c6\u30a3\u30d6\u3067\u306a\u304b\u3063\u305f\u305f\u3081\u306b\u30ed\u30b0\u30a2\u30a6\u30c8\u3055\u308c\u307e\u3057\u305f\u3002\u7d9a\u3051\u308b\u306b\u306f\u30ed\u30b0\u30a4\u30f3\u3057\u76f4\u3057\u3066\u304f\u3060\u3055\u3044\u3002", 
    "Your Progress: %(value)s%": "\u3042\u306a\u305f\u306e\u9032\u5ea6: %(value)s%", 
    "Your course begins in %(days)s day.": [
      "\u3042\u306a\u305f\u306e\u30b3\u30fc\u30b9\u306f\u3001%(days)s\u65e5\u5f8c\u306b\u59cb\u307e\u308a\u307e\u3059\u3002", 
      "\u3042\u306a\u305f\u306e\u30b3\u30fc\u30b9\u306f\u3001%(days)s\u65e5\u5f8c\u306b\u59cb\u307e\u308a\u307e\u3059\u3002"
    ], 
    "Your course hasn't begun yet. ": "\u3042\u306a\u305f\u306e\u30b3\u30fc\u30b9\u306f\u307e\u3060\u59cb\u307e\u3063\u3066\u3044\u307e\u305b\u3093\u3002", 
    "complete": "\u672a\u5b8c\u4e86", 
    "contains %s learner": [
      "%s\u5b66\u7fd2\u8005\u3092\u542b\u3080", 
      "%s\u5b66\u7fd2\u8005\u3092\u542b\u3080"
    ], 
    "course id": "\u30b3\u30fc\u30b9ID", 
    "email": "E\u30e1\u30fc\u30eb", 
    "for": "\u306b", 
    "iOS DL URL": "iOS DL URL", 
    "in the cohort!": "\u30b0\u30eb\u30fc\u30d7\u3067", 
    "one letter Friday\u0004F": "\u91d1", 
    "one letter Monday\u0004M": "\u6708", 
    "one letter Saturday\u0004S": "\u571f", 
    "one letter Sunday\u0004S": "\u65e5", 
    "one letter Thursday\u0004T": "\u6728", 
    "one letter Tuesday\u0004T": "\u706b", 
    "one letter Wednesday\u0004W": "\u6c34", 
    "same as your organization's average": "\u7d44\u7e54\u306e\u5e73\u5747\u3068\u540c\u3058", 
    "status": "\u30b9\u30c6\u30fc\u30bf\u30b9"
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
    "DATETIME_FORMAT": "Y\u5e74n\u6708j\u65e5G:i", 
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
    "DATE_FORMAT": "Y\u5e74n\u6708j\u65e5", 
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
    "FIRST_DAY_OF_WEEK": "0", 
    "MONTH_DAY_FORMAT": "n\u6708j\u65e5", 
    "NUMBER_GROUPING": "0", 
    "SHORT_DATETIME_FORMAT": "Y/m/d G:i", 
    "SHORT_DATE_FORMAT": "Y/m/d", 
    "THOUSAND_SEPARATOR": ",", 
    "TIME_FORMAT": "G:i", 
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S", 
      "%H:%M:%S.%f", 
      "%H:%M"
    ], 
    "YEAR_MONTH_FORMAT": "Y\u5e74n\u6708"
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

