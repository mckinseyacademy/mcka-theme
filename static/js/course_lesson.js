// Show Alert/Close iframes this much seconds before session time out:
const SCORM_ALERT_INTERVAL = 60;
const SCORM_IFRAME_CLOSE_INTERVAL = 30;
const SCORM_IFRAME_CLASS = '.scormxblock_hostframe';
const ALERT_MESSAGE = gettext('It looks like you\'re not active. Click OK to keep working.');
const SCORM_POPUP_IDENTIFIER = 'sco_win';
const SCORM_POPUP_FEATURES = 'alwaysLowered=1';
const REFRESH_SESSION_URL = '/accounts/refresh_user_session';

// Launch alerts
function launchAlertTimer() {
    window.setTimeout(function() {
                handleScormAlertTimeout();
                }, (getTimeoutSeconds() - SCORM_ALERT_INTERVAL) * 1000);
}

function launchPopupCloseTimer(){
    window.setTimeout(function() {
                handlePopupCloseTimeout();
                }, (getTimeoutSeconds() - SCORM_IFRAME_CLOSE_INTERVAL) * 1000);
}

// Handle alerts
function handleScormAlertTimeout() {
    if (isTimeOutValid(SCORM_ALERT_INTERVAL)) {
        showAlertOnScormPopup();
    }
    else {
        launchAlertTimer();
    }
}

function handlePopupCloseTimeout() {
    if (isTimeOutValid(SCORM_IFRAME_CLOSE_INTERVAL)) {
        saveScormDataClosePopup();
    }
    else {
        launchPopupCloseTimer();
    }
}

// Scorm spcific tasks
function showAlertOnScormPopup() {
    let scormWindow = getScormPopupReference();
    if (scormWindow) {
        scormWindow.focus();
        let didPressOk = scormWindow.confirm(ALERT_MESSAGE);
        if (didPressOk) {
            refreshUserSession();
        }
    }
}

function saveScormDataClosePopup() {
    // We save scorm data by triggering the set_raw_scorm_status call
    // The call is triggered by changing the 'src' attribute of the iframe(s)
    if (isScormPopupLaunchedBefore()) {
        $(SCORM_IFRAME_CLASS).attr('src', '');
        // Wait 100ms for set_raw_scorm_status(api call) to be fired before removing iframe
        window.setTimeout(function(){
           $(SCORM_IFRAME_CLASS).remove();
           // Wait 400ms for DOM to remove the iframe before popup close attempt is made
           window.setTimeout(function(){
           window.open('', SCORM_POPUP_IDENTIFIER, SCORM_POPUP_FEATURES).close()}, 400);
        }, 100)
    }
}

function getScormPopupReference() {
    //If a popup is open
    if (isScormPopupLaunchedBefore()) {
        // Get a reference to the popup
        var popupReference = window.open('', SCORM_POPUP_IDENTIFIER, SCORM_POPUP_FEATURES);
        // If popup is valid popup launched by the SSLA player
        if (isPopupValid(popupReference)) {return popupReference;}
        // If popup reference is invalid, close invalid popup
        popupReference.close();
    }
    return null;
}

function isScormPopupLaunchedBefore()
{
    // Get all iframes from the page hosted by the scorm xblock with popup as display type
    // non-empty src means the ssla player has been launched (popup was openend)
    var noOfPopupsOpened = $(SCORM_IFRAME_CLASS).filter("iframe[data-display_type='popup'][src!='']").length;
    return (noOfPopupsOpened > 0) ? true : false;
}

// Apros tasks
function refreshUserSession() {
    $.ajax({
      type: 'GET',
      url: REFRESH_SESSION_URL
    }).done( function(data){
        launchAlertTimer();
        launchPopupCloseTimer();
    });
}

function isPopupValid(popupReference)
{
    // If the popup is not the one launched by the SSLA player, it is invalid
    // Invalid popups maybe launched while trying to find the popup launched by user..
    // ..  (which is actually closed by user previously)
    return (popupReference.document.URL === "about:blank") ? false : true;
}

// js for gating functionality of scorm xblock

function Gating() {
    this.gatingMessage = gettext("Complete all content to continue");
}

Gating.prototype.applyGating = function() {
    var nextModuleLink = $(this.nextArrowSelector);
    if (this.isNextLinkAlreadyDisabled(nextModuleLink)) return;
    nextModuleLink.addClass(this.nextArrowDisableClass);
    nextModuleLink.attr("next-link-value", nextModuleLink.attr("href"));
    nextModuleLink.attr("href", "javascript:void(0)");
    this.addGatingMessage();
};

Gating.prototype.removeGating = function() {
    var nextModuleLink = $(this.nextArrowSelector);
    if (!this.isScormGatingApplied(nextModuleLink)) return;

    nextModuleLink.removeClass(this.nextArrowDisableClass);
    nextModuleLink.attr("href", nextModuleLink.attr("next-link-value"));
    this.removeGatingMessage();
};

Gating.prototype.isNextLinkAlreadyDisabled = function(nextModuleLink) {
    var nextLinkValue = nextModuleLink.attr("href");
    // No need to do anything since next link is already disabled
    return nextLinkValue == "#" || nextLinkValue == "javascript:void(0)" || !nextLinkValue;
};

Gating.prototype.isScormGatingApplied = function(nextModuleLink) {
    return nextModuleLink.hasClass("scorm-lock");
};


function OldUiGating() {
    Gating.call(this);
    this.nextArrowSelector = ".controls .next";
    this.nextArrowDisableClass = "complete-scorm future scorm-lock";
}

OldUiGating.prototype = Object.create(Gating.prototype);
Object.defineProperty(OldUiGating.prototype, 'constructor', {
    value: OldUiGating,
    enumerable: false, // so that it does not appear in 'for in' loop
    writable: true });

OldUiGating.prototype.addGatingMessage = function() {
    var completionPopup = document.createElement('div');
    completionPopup.className = "complete-scorm-content";
    completionPopup.innerHTML = '<i class="fa fa-lock"></i>' + this.gatingMessage;
    $(".controls .next .mcka-tooltip").prepend(completionPopup);
};

OldUiGating.prototype.removeGatingMessage = function() {
    $(".complete-scorm-content").remove()
};


function NewUiGating() {
    Gating.call(this);
    this.nextArrowSelector = ".controls .right";
    this.nextArrowTooltipSelector = this.nextArrowSelector + " span";
    this.nextArrowDisableClass = "disable scorm-lock";
    this.gatingMessageHTML = '<i class=material-icons locked>lock</i><b>' + this.gatingMessage + '<br></b>';
}

NewUiGating.prototype = Object.create(Gating.prototype);
Object.defineProperty(NewUiGating.prototype, 'constructor', {
    value: NewUiGating,
    enumerable: false,
    writable: true });

NewUiGating.prototype.addGatingMessage = function() {
    var UpdatedNextArrowTooltip = this.gatingMessageHTML + " " +this.getNextArrowToolTipContent();
    $(this.nextArrowTooltipSelector).attr("data-content", UpdatedNextArrowTooltip);
};

NewUiGating.prototype.removeGatingMessage = function() {
    var UpdatedNextArrowTooltip = this.getNextArrowToolTipContent().replace(this.gatingMessageHTML, "");
    $(this.nextArrowTooltipSelector).attr("data-content", UpdatedNextArrowTooltip);
};

NewUiGating.prototype.getNextArrowToolTipContent = function() {
    return $(this.nextArrowTooltipSelector).attr("data-content");
};

function disableNextModuleArrow() {
    isNewUI() ? new NewUiGating().applyGating() : new OldUiGating().applyGating();
}

function enableNextModuleArrow() {
    isNewUI() ? new NewUiGating().removeGating() : new OldUiGating().removeGating();
}

function isNewUI() {
    return $("body").hasClass("new-theme");
}
