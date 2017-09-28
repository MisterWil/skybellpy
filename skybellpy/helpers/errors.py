"""Errors for SkybellPy."""
USERNAME = (0, "Username must be a non-empty string")

PASSWORD = (1, "Password must be a non-empty string")

LOGIN_FAILED = (2, "Login failed")

REQUEST = (3, "Request failed")

INVALID_SETTING = (
    4, "Setting is not valid")

INVALID_SETTING_VALUE = (
    5, "Value for setting is not valid")

COLOR_VALUE_NOT_VALID = (
    6, "RGB color value is not a list of three integers between 0 and 255")

COLOR_INTENSITY_NOT_VALID = (
    7, "Intensity value is not a valid integer")
