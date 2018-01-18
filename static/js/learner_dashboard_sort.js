$(function() {
  var url = window.location.pathname + "/reorder";
  var csrftoken = $.cookie('apros_csrftoken');
  var saveSort = $("#saveSort");
  var savedSort = $("#savedSort");
  var tbody = $('tbody');
  var isDragging;
  var wasDragging;

  tbody.sortable({
    cursorAt: {
      top: 0,
      left: 0
    },
    axis: 'y'
  });

  saveSort.click("sortupdate", function(event, ui) {
    var positionList = tbody.sortable('toArray');
    $.ajax({
      dataType: 'json',
      data: {
        position: positionList,
        csrfmiddlewaretoken: csrftoken
      },
      type: 'POST',
      url: url
    });
  });
  tbody.disableSelection();

  tbody.mousedown(function() {
    isDragging = false;
  }).mousemove(function() {
    isDragging = true;
  }).mouseup(function() {
    wasDragging = isDragging;
    isDragging = false;
    if (wasDragging) {
      saveSort.css("display", "inline");
      savedSort.css("display", "none");
    }
  });

  saveSort.click(function() {
    saveSort.css("display", "none");
    savedSort.css("display", "inline");
    setTimeout(function() {
      savedSort.fadeOut("slow");
    }, 1000)
  });

  $('.confirm').click(function() {
    return window.confirm(gettext("Are you sure?"));
  });
});