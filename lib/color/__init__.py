from django.conf import settings


class Colour(object):
    def __init__(self, *args):
        """Parse the initialising argument(s) as either as: three integers
        corresponding to RGB values out of 255; an RGB tuple or list;
        a greyscale percentage; greyscale value out of 255; a 3 digit
        hexadecimal string; or a 6 digit hexadecimal string."""

        def colourConvert():
            """Post-process parsed red, green and blue values into hex"""
            r = self.red
            g = self.green
            b = self.blue
            self.hex = format(int(round(r)), "02X") + format(int(round(g)), "02X") + format(int(round(b)), "02X")
            self.rgb = (r, g, b)
            hueConvert()

        def hueConvert():
            """Calculates HSL, HSV, HSI values"""
            r = self.red / 255.
            g = self.green / 255.
            b = self.blue / 255.
            M = max(r, g, b)
            m = min(r, g, b)
            C = float(M - m)
            if C == 0:
                hue = 0
            elif M == r:
                hue = ((g - b) / C) % 6
            elif M == g:
                hue = ((b - r) / C) + 2
            elif M == b:
                hue = ((r - g) / C) + 4
            hue *= 60
            self.hue = hue
            # calculate lightness values
            L = (M + m) / 2.
            V = M
            I = (r + g + b) / 3.    # noqa: E741
            # calculate saturation values
            if C == 0:
                S_HSL = S_HSV = S_HSI = 0
            else:
                S_HSL = C / (1 - abs((2 * L) - 1))
                S_HSV = C / V
                S_HSI = 1 - (float(m) / I)
            self.hsl = (hue, S_HSL, L)
            self.hsv = (hue, S_HSV, V)
            self.hsi = (hue, S_HSI, I)

        if len(args) == 1 and type(args[0]) in [tuple, list]:
            args = args[0]
        if len(args) == 3:
            """Validate and parse RGB arguments"""
            if (max(args) > 255) or (min(args) < 0):
                raise ValueError("RGB values must be between 0 and 255")
            self.red, self.green, self.blue = args
            colourConvert()
        elif len(args) == 1 and type(args[0]) in [int, float, long]:
            """Validate greyscale input"""
            if args[0] < 0 or args[0] > 255:
                raise ValueError("Greyscale value must be either out of 1 or 255")
            if args[0] <= 1:
                self.red = self.green = self.blue = args[0] * 255
            else:
                self.red = self.green = self.blue = args[0]
            colourConvert()
        elif len(args) == 1 and type(args[0]) == str:
            """Validate hex input"""
            string = args[0]
            if len(string) in [4, 7] and string[0] == "#":
                string = string[1:]
            hexerror = "Hex string must be in the form 'RGB', '#RGB', 'RRGGBB'" \
                       " or '#RRGGBB', and each digit must be a valid hexadecimal digit"
            if len(string) not in [3, 6]:
                raise TypeError(hexerror)
            if len(string) == 3:
                try:
                    self.red = int(string[0], 16) * 17
                    self.green = int(string[1], 16) * 17
                    self.blue = int(string[2], 16) * 17
                except ValueError:
                    raise ValueError(hexerror + "3")
            elif len(string) == 6:
                try:
                    self.red = int(string[0:2], 16)
                    self.green = int(string[2:4], 16)
                    self.blue = int(string[4:6], 16)
                except ValueError:
                    raise ValueError(hexerror + "6")
            colourConvert()
        else:
            raise TypeError("Input arguments must either be 3 RGB values out "
                            "of 255, a greyscale value out of either 1 or 255, or a hexadecimal string")

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return "rgba" + self.__repr__()[6:]

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Colour({},{},{})".format(self.red, self.green, self.blue)

    def _trans(self, t, other):
        """Returns a Colour object representing the colour when the calling
        colour has a transparency of 't' out of 1 against an 'other' coloured
        background"""
        if t < 0 or t > 1:
            raise ValueError("Transparency must be between 0 and 1")
        r = (self.red * t) + (other.red * (1 - t))
        g = (self.green * t) + (other.green * (1 - t))
        b = (self.blue * t) + (other.blue * (1 - t))
        return Colour(r, g, b)

    def lighten(self, factor):
        """Returns a Colour object representing the colour when the calling
        colour is lightened by an factor of 'factor'"""
        if factor < 0 or factor > 1:
            raise ValueError("Lighten factor must be between 0 and 1")
        return Colour("FFF")._trans(factor, self)

    def darken(self, factor):
        """Returns a Colour object representing the colour when the calling
        colour is darkened by an factor of 'factor'"""
        if factor < 0 or factor > 1:
            raise ValueError("Darken factor must be between 0 and 1")
        return Colour("000")._trans(factor, self)

    def trans(self, factor):
        return self.darken(-1 * factor) if factor < 0 else self.lighten(factor)


def get_color_versions(name, value, default):
    value = str(value)
    versions = {name: value}

    try:
        color = Colour(value)
    except (ValueError, TypeError):
        color = Colour(default)
        versions = {name: default}

    versions.update({
        '{}-{}'.format(name, n): '#{}'.format(color.trans(p).hex)
        for n, p in settings.COLOR_VERSIONS.items()}
    )
    return versions


def get_branding_colors(client_customizations):
    colors = {}

    for name, default_value in settings.DEFAULT_COLORS.items():
        value = default_value
        if client_customizations:
            if name == 'primary':
                value = client_customizations.hex_course_title
            elif name == 'secondary' or name == 'header-top':
                value = client_customizations.hex_background_bar or client_customizations.hex_course_title

        colors.update(get_color_versions(name, value, default_value))

    return colors
