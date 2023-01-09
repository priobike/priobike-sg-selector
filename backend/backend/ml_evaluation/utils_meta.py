import inspect
import os


def get_filename():
    """ 
    From: https://stackoverflow.com/a/60297932 by winklerrr (CC 4.0)
    """
    # first get the full filename (including path and file extension)
    caller_frame = inspect.stack()[1]
    caller_filename_full = caller_frame.filename

    # now get rid of the directory (via basename)
    # then split filename and extension (via splitext)
    caller_filename_only = os.path.splitext(
        os.path.basename(caller_filename_full))[0]

    # return filename
    return caller_filename_only