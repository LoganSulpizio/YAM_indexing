import datetime
import pytz
import os

def write_log(message, log_file="logfile/logfile.txt"):
    # Define the Brussels/Paris time zone
    paris_tz = pytz.timezone('Europe/Paris')
    
    # Get the current time in UTC
    utc_now = datetime.datetime.now(pytz.utc)
    
    # Convert the UTC time to Brussels/Paris time
    paris_now = utc_now.astimezone(paris_tz)
    
    # Format the timestamp for the log entry
    log_timestamp = paris_now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Prepare the log message
    log_message = f"{log_timestamp}: {message}\n"
    
    if utc_now.hour % 3 == 0 and utc_now.minute % 4 == 0:

        # Check if the log file exists and its size
        if os.path.exists(log_file) and os.path.getsize(log_file) >= 3000 * 1024:  # 3000 KB
            # Format the timestamp for renaming the file
            rename_timestamp = paris_now.strftime("%Y%m%d_%H%M%S")
            
            # Generate the new file name with the timestamp
            new_log_file = f"{log_file.rsplit('.', 1)[0]}_{rename_timestamp}.txt"
            
            # Rename the current log file
            os.rename(log_file, new_log_file)
    
    # Write the log message to the (new or original) log file
    with open(log_file, "a") as file:
        file.write(log_message)

if __name__ == '__main__':
    write_log("This is a log message.")