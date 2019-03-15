/*
    This plugin darkens the color/background color of element on mouse hover.

 */

function addLight(color, amount) {
    let cc = parseInt(color, 16) + amount;
    let c = (cc > 255) ? 255 : (cc);
    c = (c.toString(16).length > 1) ? c.toString(16) : "0" + c.toString(16);
    return c;
}

/* Aclara un color hexadecimal de 6 caracteres #RRGGBB segun el porcentaje indicado */
function lighten(color, amount) {
    color = (color.indexOf("#") >= 0) ? color.substring(1, color.length) : color;
    amount = parseInt((255 * amount) / 100);
    return color = "#" + addLight(color.substring(0, 2), amount) + addLight(color.substring(2, 4), amount) + addLight(color.substring(4, 6), amount);
}

/* Resta el porcentaje indicado a un color (RR, GG o BB) hexadecimal para oscurecerlo */
function subtractLight(color, amount) {
    let cc = parseInt(color, 16) - amount;
    let c = (cc < 0) ? 0 : (cc);
    c = (c.toString(16).length > 1) ? c.toString(16) : "0" + c.toString(16);
    return c;
}

/* Oscurece un color hexadecimal de 6 caracteres #RRGGBB segun el porcentaje indicado */
function darken(color, amount) {
    color = (color.indexOf("#") >= 0) ? color.substring(1, color.length) : color;
    amount = parseInt((255 * amount) / 100);
    return color = "#" + subtractLight(color.substring(0, 2), amount) + subtractLight(color.substring(2, 4), amount) + subtractLight(color.substring(4, 6), amount);
}


function rgb2hex(rgb) {
    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);

    function hex(x) {
        return ("0" + parseInt(x).toString(16)).slice(-2);
    }

    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
}


// ome = on mouse event
// dome = darken on mouse event
$(".ome").mouseenter(function (e) {
    e = e || window.event;

    var target;
    var colorProp;
    var sel = $(e.currentTarget);
    if (sel.hasClass('dome-bc')) {
        target = sel;
        colorProp = 'background-color';
    } else if (sel.hasClass('dome-c')) {
        target = sel;
        colorProp = 'color';
    } else {
        var child = $(e.currentTarget).children('.dome-bc');
        if (child.length > 0) {
            target = child;
            colorProp = 'background-color';
        }

        child = $(e.currentTarget).children('.dome-c');
        if (child.length > 0) {
            target = child;
            colorProp = 'color';
        }
    }

    var dc = target.attr('dc');
    if (dc !== undefined) {
        target.css(colorProp, dc);
        return;
    }

    var oc = target.css(colorProp);
    if (oc !== undefined && oc !== 'rgba(0, 0, 0, 0)') {
        oc = rgb2hex(oc);
        dc = darken(oc, 25);
        target.attr('oc', oc);
        target.attr('dc', dc);
        target.css(colorProp, dc);
    }
}).mouseleave(function (e) {
    e = e || window.event;
    var target;
    var colorProp;
    var sel = $(e.currentTarget);
    if (sel.hasClass('dome-bc')) {
        target = sel;
        colorProp = 'background-color';
    } else if (sel.hasClass('dome-c')) {
        target = sel;
        colorProp = 'color';
    } else {
        var child = $(e.currentTarget).children('.dome-bc');
        if (child.length > 0) {
            target = child;
            colorProp = 'background-color';
        }

        child = $(e.currentTarget).children('.dome-c');
        if (child.length > 0) {
            target = child;
            colorProp = 'color';
        }
    }

    var oc = target.attr('oc');
    if (oc !== undefined) {
        target.css(colorProp, oc);
    }
});

if (secondary !== undefined && secondary !== 'rgba(0, 0, 0, 0)') {
    $('.visualization .filled.band-2').css('background-color', lighten(secondary, 50));
    $('.visualization .filled.total').css('background-color', darken(secondary, 50));
}

if (typeof lighten !== "undefined" && primary != null) {
    $('.bbGrid-container thead, .primaryBgLighten').css('background-color', lighten(primary, 60));

    //  Using primary lighten color for description area of lessons page.
}

//  Course landing pagelesson bar hover bg color
if (secondary !== undefined) {
    $('.courseRow a.description').css('background-color', lighten(secondary, 90));
    $('.courseRow .bookmark.primary svg path').css('fill', lighten(secondary, 0));
}

//  Course landing pagelesson bar hover bg color
if (secondary !== undefined) {
    $('.courseRow a.description').css('background-color', lighten(secondary, 90));
    $('.courseRow .bookmark.primary svg path').css('fill', lighten(secondary, 0));
}





