""" Maths helpers """


def round_to_int(value):
    """
    Rounds a value and convert to integer

    e.g; 0.002 -> 0
         0.6 -> 1
    """
    return int(round(value))


def round_to_int_bump_zero(value):
    """
    Rounds a value and convert to integer
    return 1 if rounded value is < 0
    """
    rounded_value = round_to_int(value)

    if rounded_value < 1 and value > 0:
        rounded_value = 1

    return rounded_value


def calculate_percentage(part, whole):
    """
    Calculates what percentage part is of whole

    e.g; calculate_percentage(25, 75) -> 33
         calculate_percentage(23, 30) -> 77
    """
    percentage = (100.0 / (whole or 1)) * part

    return round_to_int_bump_zero(percentage)
