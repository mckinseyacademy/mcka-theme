Apros.views.CourseProgress = Backbone.View.extend({
  initialize: function() {
  },

  render: function() {
  }

});

// Progress Total and Cohort Average indicator for RTL

$(document).ready(function(){
  var progressTotal = $(".rtl .course-progress .visualization .total");
  var cohortPointer = $(".rtl .course-progress .visualization .triangle");
  $(progressTotal).css("right", progressTotal.css('left'));
  $(cohortPointer).css("right", cohortPointer.css('left'));
});
