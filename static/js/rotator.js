(function () {

  var rotator = $('.rotator');
  var cardCount = parseInt(rotator.attr('data-count'));
  var bookmarkIndex = parseInt(rotator.attr('data-bookmark-index'));
  var btnLeft = rotator.find('.nav-left');
  var btnRight = rotator.find('.nav-right');
  var slides = rotator.find('.slides');


  $(document).ready(function () {

    var perSection = Math.floor(rotator.width() / slides.find('li').outerWidth(true));
    var widthPerc = 100/perSection;
    var cardIndex = 0;

    var middle = Math.ceil(perSection/2);

    // try to center the boomarked card
    if (bookmarkIndex < middle) {
      cardIndex = 0;
    }
    else if (bookmarkIndex > cardCount-middle) {
      cardIndex = cardCount - perSection;
    }
    else {
      cardIndex = bookmarkIndex - middle + 1;
    }

    slide(-cardIndex * widthPerc);
    toggleNavButtons();

    requestAnimationFrame(function () {
      slides.addClass('animate').css('visibility', 'visible');
    });

    btnLeft.on('click', function() {
      var delta = cardIndex;
      if (delta > perSection) {
        delta = perSection;
      }
      if (delta > 0) {
        cardIndex -= delta;
        slide(-cardIndex * widthPerc);
        toggleNavButtons();
      }
    });

    btnRight.on('click', function() {
      var delta = cardCount - cardIndex - perSection;
      if (delta > perSection) {
        delta = perSection;
      }
      if (delta > 0) {
        cardIndex += delta;
        slide(-cardIndex * widthPerc);
        toggleNavButtons();
      }
    });


    function toggleNavButtons() {
      var leftDelta = cardIndex;
      var rightDelta = cardCount - cardIndex - perSection;
      leftDelta > 0 ? btnLeft.show() : btnLeft.hide();
      rightDelta > 0 ? btnRight.show() : btnRight.hide();
    }

  });


  function slide(positionPerc) {
    requestAnimationFrame(function () {
      slides.css('margin-left', positionPerc + '%');
    });
  }

})();
