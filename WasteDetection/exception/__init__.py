import sys

def error_message_details(error):
    _, _, exc_tb = sys.exc_info()

    if exc_tb is not None:
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_no = exc_tb.tb_lineno
        error_message = f"Error occurred in: {file_name} -> Line: {line_no} -> {str(error)}"
    else:
        error_message = f"Error occurred: {str(error)}"

    return error_message

class AppException(Exception):
    def __init__(self, error_message):
        """
        :param error_message: error message in string format
        """
        super().__init__(error_message)

        self.error_message = error_message_details(error_message)

    def __str__(self):
        return self.error_message