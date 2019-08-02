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

/*function to check hexadecimal value*/
function isHex(h) {
    var a = parseInt(h,16);
    return (a.toString(16) === h)
}

/* function to convert hex value to rgb*/
function hexToRgb(hex) {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function(m, r, g, b) {
        return r + r + g + g + b + b;
    });

    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

/* function to convert rgb value to hex*/
function rgb2hex(rgb) {
    function hex(x) {
        return ("0" + parseInt(x).toString(16)).slice(-2);
    }
    if (isHex(rgb.substr(1)))
    {
        return "#" + hex(hexToRgb(rgb).r) + hex(hexToRgb(rgb).g) + hex(hexToRgb(rgb).b);
        //return '#2042cb';
    }
    else
    {
        rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
        return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
    }

}

// ome = on mouse event
// dome = darken on mouse event
$(document).on('mouseenter', '.ome', function (e) {
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
    } else if (sel.hasClass('dome-f')) {
        target = sel;
        colorProp = 'fill';
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

        child = $(e.currentTarget).find('.dome-f');
        if (child.length > 0) {
            target = child;
            colorProp = 'fill';
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
});

$(document).on('mouseleave', '.ome', function (e) {
    e = e || window.event;
    var target;
    var colorProp;
    var sel = $(e.currentTarget);
    if(sel.hasClass('dome-active'))
        return
    if (sel.hasClass('dome-bc')) {
        target = sel;
        colorProp = 'background-color';
    } else if (sel.hasClass('dome-c')) {
        target = sel;
        colorProp = 'color';
    } else if (sel.hasClass('dome-f')) {
        target = sel;
        colorProp = 'fill';
    }else {
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

        child = $(e.currentTarget).find('.dome-f');
        if (child.length > 0) {
            target = child;
            colorProp = 'fill';
        }
    }

    var oc = target.attr('oc');
    if (oc !== undefined) {
        target.css(colorProp, oc);
    }
});

if (window.secondary) {
    $('.visualization .filled.band-2').css('background-color', lighten(secondary, 60));
    $('.visualization .filled.total').css('background-color', darken(secondary, 30));

  //  Course landing pagelesson bar hover bg color
    $('.courseRow a.description').css('background-color', lighten(secondary, 60));
    $('.courseRow .bookmark.primary svg path').css('fill', lighten(secondary, 0));
}
