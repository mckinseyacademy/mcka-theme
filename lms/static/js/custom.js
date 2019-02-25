
$('.new-theme input[type="checkbox"]') .change(function(event) {
 
    if (event.target.checked) {
      console.log('checked')
      $(event.target).parent().addClass("selected")
    } else {
      console.log('not checked')
      $(event.target).parent().removeClass("selected")
    }
  });
