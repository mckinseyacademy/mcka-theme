$(document).ready(function () {

    if($(".reset-password #id_email").val() !== "")
    {
        $('#reset-password-submit').attr("disabled", false);
        $(".reset-password #id_email").parents('.form-group').addClass('focused');
    }


    $("#login_id").on("keyup", function () {
        $('#login').attr("disabled", false);
        var user_name = $(".user_name_element");
        $(user_name).removeClass("success").removeClass("error");
        $(this).get(0).setCustomValidity("");
        var password = $(".user_password_element");
        if(!$(password).hasClass("d-none")) {
            $(password).addClass("d-none");
            $('.forgot-pswd-link').toggleClass('d-none');
            $(".login-page").removeClass("login-with-password");
            $("input[name=password]").val("");
        }
    });

    $(".reset-password #id_email").on("keyup", function ()
    {
        $('#reset-password-submit').attr("disabled", false);
    });

    $("#password").on("keyup", function () {
        $('#login').attr("disabled", false);
        var user_password = $(".user_password_element");
        $(user_password).removeClass("success").removeClass("error");
        $(this).get(0).setCustomValidity("");
    });

    $('#password-reset-done, #password-reset-complete, #password-reset-failed').on('hidden.bs.modal', function () {
        if(window.location.href.indexOf("?"))
            window.location.href =  window.location.href.split("?")[0];
    });

    if ($(window).width() < 992 && $('.leaderboards-list .col').length === 3) {
        $('.leaderboards-list .col').removeClass('col').addClass('col-12');
    }

    $('#pnProductNavContents>ul> li').not(":has(.dropdown-menu, .dropdown-toggle)").click(function() {
        $('#pnProductNavContents>ul> li.active').removeClass('active');
        $(this).addClass('active');
    });

    $('.headerNav>ul>li').click(function() {
        $('.headerNav>ul>li.active').removeClass('active');
        $(this).addClass('active');
    });


    $("#lessons-content").on('click', function(e) {
        if ($(e.target).hasClass('load-course-lessons')) {
            var course_id = $(e.target).data('course-id');
            $.ajax({
                url: '/courses/' + course_id + '/course_lessons_menu',
                method: 'GET',
                contentType: 'text/html'
            }).done(function(data, status, xhr) {
                if (xhr.status == 200) {
                    $('.allLessons').html(data);
                    $(e.target).removeClass('load-course-lessons');
                    $(e.target).attr("data-toggle", "dropdown");
                    $(e.target).dropdown('toggle');
                }
            });
        }
    });


    // ================   Trigger for the Notification dropdown content   ==================
    $(window).on('show.bs.dropdown', function (e) {
        if ($(e.target).hasClass('notifications')){
            $('.xns-icon').trigger('click');
        }
        else{
            $('.notifications .dropdown-menu').hide();
        }
        $(e.target).parents('.courseNavWrap, .mainNav.headerNav').addClass('nav-active');
    });
    $(window).on('hide.bs.dropdown', function (e) {
        if ($(e.target).hasClass('notifications')){
            $('.notifications .dropdown-menu').hide();
        }
        $(e.target).parents('.courseNavWrap').removeClass('nav-active');
    });
    $('#user').addClass('active');


    $('#password ~ input').focus(function() {
        $('#password').addClass('active');
    });

    var isMobile = (/android|webos|iphone|com.mcka.RNApp|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
    $('#show-hide, .show-hide').click(function () {
        if (isMobile){
            return
        }

        var text = $(this).text();
        if (text == 'visibility_off') {
            $(this).text('visibility');
            $(this).siblings("input").attr('type', 'text');
            $(this).attr("data-content", gettext("Hide password"));
        }
        else {
            $(this).text('visibility_off');
            $(this).siblings("input").attr('type', 'password');
            $(this).attr("data-content", gettext("Show password"));
        }
    });


    //Input Placeholder become label

    $('input').focus(function() {
        $(this).parents('.form-group').addClass('focused');
    });

    $('input').blur(function() {
        var inputValue = $(this).val();
        if (inputValue == "") {
            $(this).removeClass('filled');
            $(this).parents('.form-group').removeClass('focused');
            $('#login').attr('disabled', 'disabled');
            $('#reset-password-submit').attr("disabled", 'disabled');
            $('#reset-password-done').attr("disabled", "disabled");
        } else {
            $(this).addClass('filled');
        }
    });

    //End Input Placeholder become label

    //Form label animation
    $('#user ~ input').focus(function() {
        $('#user').addClass('active');
    });


    //    Add/Remove class on Need Help link on mobile
    $(".login .helpLink").click(function() {
        var self = $(this).parent();
        self.toggleClass("show-links");

        $('html,body').animate({
            scrollTop: $(".login .quick-links").offset().bottom
        }, 800);
        alert
    });


    // Custom style for Input File ======================
    $('#chooseFile').bind('change', function() {
        var filename = $("#chooseFile").val();
        if (/^\s*$/.test(filename)) {
            $(".file-upload").removeClass('active');
            $("#noFile").text("No file selected");
        } else {
            $(".file-upload").addClass('active');
            $("#noFile").text(filename.replace("C:\\fakepath\\", ""));
        }
    });

    // End of Custom style for Input File ===============


    $(function() {
        $('[data-toggle="popover"]').popover();
    });
    //    Add and Remove Class on body for Lesson Overview page
    var removeClass = true;
    // when clicking the button : toggle the class, tell the background to leave it as is
    $(".zoomWrap").click(function() {
        $("body").toggleClass('zoomIn');
        removeClass = false;
        $.cookie(cookie_key, $("body").hasClass('zoomIn'), { path: '/' });
        $('.longTapPopover').popover('hide');
    });
    // when clicking the div : never remove the class
    $(".zoomWrap").click(function() {
        removeClass = false;
        $(".appHeader").removeClass('delay-1s');
        $(".learner-nav").removeClass('delay-2s');
        $("footer").removeClass('delay-3s');
    });
    // when click event reaches "html" : remove class if needed, and reset flag
    $("html").click(function() {
        if (removeClass) {
            $(".toggletag").removeClass('zoomIn');
        }
        removeClass = true;
    });
    //    End Add and Remove Class on body for Lesson Overview page


    // ============= Adding Smooth Scrolling to Sections =================
    // ====https://css-tricks.com/snippets/jquery/smooth-scrolling/====
    // Select all links with hashes
    $('a[href*="#"]')
        // Remove links that don't actually link to anything
        .not('[href="#"]')
        .not('[href="#0"]')
        .click(function(event) {
            // On-page links
            if (
                location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') &&
                location.hostname == this.hostname
            ) {
                // Figure out element to scroll to
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                // Does a scroll target exist?
                if (target.length) {
                    // Only prevent default if animation is actually gonna happen
                    event.preventDefault();
                    $('html, body').animate({
                        scrollTop: target.offset().top
                    }, 1000, function() {
                        // Callback after animation
                        // Must change focus!
                        var $target = $(target);
                        $target.focus();
                        if ($target.is(":focus")) { // Checking if the target was focused
                            return false;
                        } else {
                            $target.attr('tabindex', '-1'); // Adding tabindex for elements not focusable
                            $target.focus(); // Set focus again
                        };
                    });
                }
            }
        });


    switch ($('table.progress-data td.progress_data_col').length) {

        case 1:
            $('table.progress-data').addClass('table-col-1');
            break;

        case 2:
            $('table.progress-data').addClass('table-col-2');
            break;

        case 3:
            $('table.progress-data').addClass('table-col-3');
            break;
    }


    // Future course modal

    $(".future-course #course-navigation").attr("href", "javascript:void()");
    $(".future-course .card-body").removeClass("dome-bc");


    // Add spinner to crop & save button of profile upload
    $("#crop-save").click(function () {
        $("#crop-save #spinner").addClass("spinner-border-sm").addClass("spinner-border");
    });


    $('.carousel').carousel({
        keyboard: false
      });

    //  New featre Modal (disable scrolling on body)
    $('.carousel-control-next').click(function(){
        $('.carousel-item').removeClass("next");
        $('.carousel-item').removeClass("prev");
        $('.carousel-item.active').addClass("next");
        $('.carousel').carousel('next')
        $('.carousel-item.active').addClass("next");
        $('.carousel-inner').removeClass("nextSlide");
        $('.carousel-inner').removeClass("prevSlide");
        $('.carousel-inner').addClass("nextSlide");
    });

    $('.carousel-control-prev').click(function(){
        $('.carousel-item').removeClass("prev");
        $('.carousel-item').removeClass("next");
        $('.carousel-item.active').addClass("prev");
        $('.carousel').carousel('prev')
        $('.carousel-item.active').addClass("prev");
        $('.carousel-inner').removeClass("nextSlide");
        $('.carousel-inner').removeClass("prevSlide");
        $('.carousel-inner').addClass("prevSlide");
    });
    //  KeyBoard Controls Activation For New FeatureTour Modal
    jQuery(document).bind('keyup', function (e) {
        if (e.keyCode == 39) {
            jQuery('.carousel-control-next').trigger('click');
        }
        else if (e.keyCode == 37) {
            jQuery('.carousel-control-prev').trigger('click');
        }
    });

    if ($(window).width() <= 1024 && $('.progress-data tr td').length >= 2) {
        $(".progress-data").addClass("three-cols");
    }
});


//Main Navigation animation Js ===== https://codepen.io/benfrain/pen/zZZLaP =====

$(window).on('resize load', function() {
    smoothNavLinks();
});

function smoothNavLinks() {
    var SETTINGS = {
        navBarTravelling: false,
        navBarTravelDirection: "",
        navBarTravelDistance: 150
    };

    var activeColours = "#2E2D39";

    document.documentElement.classList.remove("no-js");
    document.documentElement.classList.add("js");

    // Out advancer buttons
    var pnAdvancerLeft = document.getElementById("pnAdvancerLeft");
    var pnAdvancerRight = document.getElementById("pnAdvancerRight");
    // the indicator
    var pnIndicator = document.getElementById("pnIndicator");

    var pnProductNav = document.getElementById("pnProductNav");
    var pnProductNavContents = document.getElementById("pnProductNavContents");

    // pnProductNav.setAttribute("data-overflowing", determineOverflow(pnProductNavContents, pnProductNav));


    // Handle the scroll of the horizontal container
    var last_known_scroll_position = 0;
    var ticking = false;

    function doSomething(scroll_pos) {
        overflow_value = determineOverflow(pnProductNavContents, pnProductNav);
        pnProductNav.setAttribute("data-overflowing", overflow_value);
        if(overflow_value == 'both') {
            pnAdvancerLeft.classList.add('active');
            pnAdvancerRight.classList.add('active');
        }
        else if(overflow_value == "right") {
            pnAdvancerRight.classList.add('active');
            pnAdvancerLeft.classList.remove('active');
        }
        else {
            pnAdvancerRight.classList.remove('active');
            pnAdvancerLeft.classList.add('active');
        }
    }

    pnProductNav && pnProductNav.addEventListener("scroll", function() {
        last_known_scroll_position = window.scrollY;
        if (!ticking) {
            window.requestAnimationFrame(function() {
                doSomething(last_known_scroll_position);
                ticking = false;
            });
        }
        ticking = true;
    });


    pnAdvancerLeft && pnAdvancerLeft.addEventListener("click", function() {
        // If in the middle of a move return
        if (SETTINGS.navBarTravelling === true) {
            return;
        }
        // If we have content overflowing both sides or on the left
        if (determineOverflow(pnProductNavContents, pnProductNav) === "left" || determineOverflow(pnProductNavContents, pnProductNav) === "both") {
            // Find how far this panel has been scrolled
            var availableScrollLeft = pnProductNav.scrollLeft;
            // If the space available is less than two lots of our desired distance, just move the whole amount
            // otherwise, move by the amount in the settings
            if (availableScrollLeft < SETTINGS.navBarTravelDistance * 2) {
                pnProductNavContents.style.transform = "translateX(" + availableScrollLeft + "px)";
                pnAdvancerLeft.classList.remove('active');
                pnAdvancerRight.classList.add('active');
            } else {
                pnAdvancerLeft.classList.add('active');
                pnAdvancerRight.classList.add('active');
                pnProductNavContents.style.transform = "translateX(" + SETTINGS.navBarTravelDistance + "px)";
            }
            // We do want a transition (this is set in CSS) when moving so remove the class that would prevent that
            pnProductNavContents.classList.remove("pn-ProductNav_Contents-no-transition");
            // Update our settings
            SETTINGS.navBarTravelDirection = "left";
            SETTINGS.navBarTravelling = true;
        }
        // Now update the attribute in the DOM
        pnProductNav.setAttribute("data-overflowing", determineOverflow(pnProductNavContents, pnProductNav));
    });

    pnAdvancerRight && pnAdvancerRight.addEventListener("click", function() {
        // If in the middle of a move return
        if (SETTINGS.navBarTravelling === true) {
            return;
        }
        // If we have content overflowing both sides or on the right
        if (determineOverflow(pnProductNavContents, pnProductNav) === "right" || determineOverflow(pnProductNavContents, pnProductNav) === "both") {
            // Get the right edge of the container and content
            var navBarRightEdge = pnProductNavContents.getBoundingClientRect().right;
            var navBarScrollerRightEdge = pnProductNav.getBoundingClientRect().right;
            // Now we know how much space we have available to scrollq
            var availableScrollRight = Math.floor(navBarRightEdge - navBarScrollerRightEdge);
            // If the space available is less than two lots of our desired distance, just move the whole amount
            // otherwise, move by the amount in the settings
            if (availableScrollRight < SETTINGS.navBarTravelDistance * 2) {
                pnProductNavContents.style.transform = "translateX(-" + availableScrollRight + "px)";
                pnAdvancerRight.classList.remove('active');
                pnAdvancerLeft.classList.add('active');

            } else {
                pnAdvancerLeft.classList.add('active');
                pnAdvancerRight.classList.add('active');
                pnProductNavContents.style.transform = "translateX(-" + SETTINGS.navBarTravelDistance + "px)";
            }
            // We do want a transition (this is set in CSS) when moving so remove the class that would prevent that
            pnProductNavContents.classList.remove("pn-ProductNav_Contents-no-transition");
            // Update our settings
            SETTINGS.navBarTravelDirection = "right";
            SETTINGS.navBarTravelling = true;
        }
        // Now update the attribute in the DOM
        pnProductNav.setAttribute("data-overflowing", determineOverflow(pnProductNavContents, pnProductNav));
    });

    pnProductNavContents && pnProductNavContents.addEventListener(
        "transitionend",
        function() {
            // get the value of the transform, apply that to the current scroll position (so get the scroll pos first) and then remove the transform
            var styleOfTransform = window.getComputedStyle(pnProductNavContents, null);
            var tr = styleOfTransform.getPropertyValue("-webkit-transform") || styleOfTransform.getPropertyValue("transform");
            // If there is no transition we want to default to 0 and not null
            var amount = Math.abs(parseInt(tr.split(",")[4]) || 0);
            pnProductNavContents.style.transform = "none";
            pnProductNavContents.classList.add("pn-ProductNav_Contents-no-transition");
            // Now lets set the scroll position
            if (SETTINGS.navBarTravelDirection === "left") {
                pnProductNav.scrollLeft = pnProductNav.scrollLeft - amount;
            } else {
                pnProductNav.scrollLeft = pnProductNav.scrollLeft + amount;
            }
            SETTINGS.navBarTravelling = false;
        },
        false
    );

    // Handle setting the currently active link
    pnProductNavContents && pnProductNavContents.addEventListener("click", function(e) {

        var links = [].slice.call(document.querySelectorAll(".pn-ProductNav_Link"));
        links.forEach(function (item) {
            item.setAttribute("aria-selected", "false");
        })
        e.target.setAttribute("aria-selected", "true");
        // Pass the clicked item and it's colour to the move indicator function
        moveIndicator(e.target, activeColours[links.indexOf(e.target)]);
    });

    // var count = 0;
    function moveIndicator(item, color) {
        // console.log('item ', item.nodeName);
        if (item.nodeName !== 'A') {
            return false;
        }

        var textPosition = item.getBoundingClientRect();
        var container = pnProductNavContents.getBoundingClientRect().left;
        var distance = textPosition.left - container;
        var scroll = pnProductNavContents.scrollLeft;
        pnIndicator.style.transform = "translateX(" + (distance + scroll) + "px) scaleX(" + textPosition.width * 0.01 + ")";
        // count = count += 100;
        // pnIndicator.style.transform = "translateX(" + count + "px)";

        if (color) {
            pnIndicator.style.backgroundColor = color;
        }
    }

    function determineOverflow(content, container) {
        var containerMetrics = container.getBoundingClientRect();
        var containerMetricsRight = Math.floor(containerMetrics.right);
        var containerMetricsLeft = Math.floor(containerMetrics.left);
        var contentMetrics = content.getBoundingClientRect();
        var contentMetricsRight = Math.floor(contentMetrics.right);
        var contentMetricsLeft = Math.floor(contentMetrics.left);
        var language_dir = $('html').attr('dir');
        if(language_dir == 'rtl')
            contentMetricsLeft += 1
        if (containerMetricsLeft > contentMetricsLeft && containerMetricsRight < contentMetricsRight) {
            return "both";
        } else if (contentMetricsLeft < containerMetricsLeft) {
            return "left";
        } else if (contentMetricsRight > containerMetricsRight) {
            return "right";
        } else {
            return "none";
        }
    }

    /**
     * @fileoverview dragscroll - scroll area by dragging
     * @version 0.0.8
     *
     * @license MIT, see https://github.com/asvd/dragscroll
     * @copyright 2015 asvd <heliosframework@gmail.com>
     */


    (function(root, factory) {
        if (typeof define === 'function' && define.amd) {
            define(['exports'], factory);
        } else if (typeof exports !== 'undefined') {
            factory(exports);
        } else {
            factory((root.dragscroll = {}));
        }
    }(this, function(exports) {
        var _window = window;
        var _document = document;
        var mousemove = 'mousemove';
        var mouseup = 'mouseup';
        var mousedown = 'mousedown';
        var EventListener = 'EventListener';
        var addEventListener = 'add' + EventListener;
        var removeEventListener = 'remove' + EventListener;
        var newScrollX, newScrollY;

        var dragged = [];
        var reset = function(i, el) {
            for (i = 0; i < dragged.length;) {
                el = dragged[i++];
                el = el.container || el;
                el[removeEventListener](mousedown, el.md, 0);
                _window[removeEventListener](mouseup, el.mu, 0);
                _window[removeEventListener](mousemove, el.mm, 0);
            }

            // cloning into array since HTMLCollection is updated dynamically
            dragged = [].slice.call(_document.getElementsByClassName('dragscroll'));
            for (i = 0; i < dragged.length;) {
                (function(el, lastClientX, lastClientY, pushed, scroller, cont) {
                    (cont = el.container || el)[addEventListener](
                        mousedown,
                        cont.md = function(e) {
                            if (!el.hasAttribute('nochilddrag') ||
                                _document.elementFromPoint(
                                    e.pageX, e.pageY
                                ) == cont
                            ) {
                                pushed = 1;
                                lastClientX = e.clientX;
                                lastClientY = e.clientY;

                                e.preventDefault();
                            }
                        }, 0
                    );

                    _window[addEventListener](
                        mouseup, cont.mu = function() {
                            pushed = 0;
                        }, 0
                    );

                    _window[addEventListener](
                        mousemove,
                        cont.mm = function(e) {
                            if (pushed) {
                                (scroller = el.scroller || el).scrollLeft -=
                                    newScrollX = (-lastClientX + (lastClientX = e.clientX));
                                scroller.scrollTop -=
                                    newScrollY = (-lastClientY + (lastClientY = e.clientY));
                                if (el == _document.body) {
                                    (scroller = _document.documentElement).scrollLeft -= newScrollX;
                                    scroller.scrollTop -= newScrollY;
                                }
                            }
                        }, 0
                    );
                })(dragged[i++]);
            }
        }


        if (_document.readyState == 'complete') {
            element = document.querySelector("div.mainNav li.active a.nav-link");
            if(element) {
                var links = [].slice.call(document.querySelectorAll(".pn-ProductNav_Link"));
                overflow_value = determineOverflow(element, pnProductNav);
                if (overflow_value == 'right')
                    $('#pnProductNav').animate({
                        scrollLeft: $(element).offset().left - 40
                    });
                else if (overflow_value == 'left')
                    $('#pnProductNav').animate({
                        scrollLeft: $(element).offset().top + 95
                    });
            }
            reset();
        } else {
            _window[addEventListener]('load', reset, 0);
        }

        exports.reset = reset;
    }));

}

smoothNavLinks();


$(window).on("load", function () {

    setTimeout(function () {
        $(".login").trigger('click');
        let value = $("input[type='text'], input[type='password']").val();
        if (value && value.length > 0) {
            $("input[type='text'], input[type='password']").trigger("click");
        }
     }, 2000);

    // Preloaders for platform
    $('.loader').removeClass("donut-loader").removeClass("loader");
    $('.preloader').removeClass("preloader");
    $('.courseLanding .contentCard').css("visibility", "visible");
    $('.courseLanding').removeClass('skeleton');


    // Remove spinner from crop & save button
    $("#crop-save #spinner").removeClass("spinner-border-sm").removeClass("spinner-border");

    // Cover images with width & height of their parent
    $('div.faculty label').each(function (index) {
        scaleImage(this);
    });
});

// Preloader for courses page

$('.my-courses .card').click(function () {
    $('.my-courses .card').removeClass("loader").removeClass("donut-loader");
    $(this).addClass("loader").addClass("donut-loader");
});

"use strict";
function scaleImage(label) {
    var scaler;
    var imgWidth = $(label).find("img").width();
    var imgHeight = $(label).find("img").height();
    var stageW = $(label).width();
    var stageH = $(label).height();
    if (stageH / stageW > imgHeight / imgWidth) {
        scaler = imgWidth / imgHeight;
        imgWidth = stageH * scaler;
        $(label).find("img").css("width", imgWidth)
        $(label).find("img").css("height", "auto")
    } else {
        scaler = imgHeight / imgWidth;
        imgHeight = stageW * scaler;
        $(label).find("img").css("height", imgHeight)
        $(label).find("img").css("width", "auto")
    }
}


$(window).resize(function () {
    $('div.faculty label').each(function (index) {
        scaleImage(this);
    });
});
