import sys
import traceback
from script.Utilities.write_logs import write_log
from script.Utilities.send_telegram import send_telegram

def handle_keyboard_exception(log_message, logfile):
    print(" Execution interrupted")
    write_log(log_message, logfile)
    sys.exit(0)

def handle_exception(e, error_message, logfile_path, send_telegram_bool = True, stop_script = False):
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb)
    relevant_tb = [frame for frame in tb if frame.filename == __file__]
    
    if relevant_tb:
        filename, lineno, funcname, text = relevant_tb[-1]
    else:
        filename, lineno, funcname, text = tb[-1]
    
    if send_telegram_bool:
        error_message_str = '{}:\n{}\nLine number: {}\n{}'.format(error_message, e, lineno, text)
        send_telegram(error_message_str)
    write_log(traceback.format_exc(), logfile_path)
    if stop_script:
        raise e