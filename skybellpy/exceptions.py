"""The exceptions used by SkybellPy."""


class SkybellException(Exception):
    """Class to throw general skybell exception."""

    def __init__(self, error, details=None):
        """Initialize SkybellException."""
        # Call the base class constructor with the parameters it needs
        super(SkybellException, self).__init__(
            '{}: {}'.format(error[1], details))

        self.errcode = error[0]
        self.message = error[1]
        self.details = details


class SkybellAuthenticationException(SkybellException):
    """Class to throw authentication exception."""

    pass
