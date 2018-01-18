$(function() {
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

  $("#saveSortDiscover").click("sortupdate", function(event, ui) {
    $.ajax({
      dataType: 'json',
      headers: {
        'X-CSRFToken': $.cookie('apros_csrftoken')
      },
      data: {
        position: $("#discover-body").sortable('toArray')
      },
      type: 'POST',
      url: window.location.pathname + "/discover/list/reorder"
    });

    $("#saveSortDiscover").css("display", "none");
    $("#savedSortDiscover").css("display", "inline");
    setTimeout(function() {
      $("#savedSortDiscover").fadeOut("slow");
    }, 1000)
  });

  $("#saveSortElement").click("sortupdate", function(event, ui) {
    $.ajax({
      dataType: 'json',
      headers: {
        'X-CSRFToken': $.cookie('apros_csrftoken')
      },
      data: {
        position: $("#element-body").sortable('toArray')
      },
      type: 'POST',
      url: window.location.pathname + "/element_reorder"
    });

    $("#saveSortElement").css("display", "none");
    $("#savedSortElement").css("display", "inline");
    setTimeout(function() {
      $("#savedSortElement").fadeOut("slow");
    }, 1000)
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
      $("#saveSortElement").css("display", "inline");
      $("#saveSortDiscover").css("display", "inline");
      $("#savedSortElement").css("display", "none");
      $("#savedSortDiscover").css("display", "none");
    }
  });

  $('.confirm').click(function() {
    return window.confirm(gettext("Are you sure?"));
  });
});
