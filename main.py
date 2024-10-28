import os
import time
import json
from web3 import Web3
from script.get_and_decode_logs_YAM import get_log_YAM_https, decode_logs_YAM
from script.export_logs import export_logs_to_bot
from script.add_event_to_db import add_events_to_db
from script.index_logs_manually import index_manually
from script.Utilities.contract_data import contract_data
from script.Utilities.write_logs import write_log
from script.Utilities.handle_exception import handle_keyboard_exception, handle_exception


def main():

    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)

    w3 = [Web3(Web3.HTTPProvider(config[f'w3_url{i}'])) for i in range(1, 5)]

    db_path = config['db_path']
    path_export_logs = config['path_export_logs']

    BLOCK_TO_RETRIEVE = config['BLOCK_TO_RETRIEVE']         # Number of block to retrieve from the W3 RPC by HTTP request 
    COUNT_BEFORE_RESYNC = config['COUNT_BEFORE_RESYNC']     # Number of retrieve before resynchronizing to the latest block
    BLOCK_BUFFER = config['BLOCK_BUFFER']                   # Gap between the latest block available and what is actually retrieve
    TIME_TO_WAIT_BEFORE_RETRY = config['TIME_TO_WAIT_BEFORE_RETRY'] # time to wait before retry when RPC is not available

    w3_main = 0
    w3_backup = 1

    print('running YAM indexing...')
    write_log("index YAM started", 'logfile/logfile_indexingYAM.txt')

    current_block_number = w3[0].eth.block_number
    from_block = current_block_number - BLOCK_BUFFER - BLOCK_TO_RETRIEVE + 1
    to_block = current_block_number - BLOCK_BUFFER

    sync_counter = unsuccessful_request_counter  = counter_backup = 0

    index_manually(w3[0], contract_data['YAM']['address'], from_block-20, from_block-1, 5, db_path)

    while True:

        try:

            start_time = time.time()

            unsuccessful_request_counter += 1

            logs = get_log_YAM_https(w3[w3_main], contract_data['YAM']['address'], from_block, to_block)
            logs_backup = get_log_YAM_https(w3[w3_backup], contract_data['YAM']['address'], from_block, to_block, True)

            unsuccessful_request_counter = 0


            decoded_logs = decode_logs_YAM(logs + logs_backup)

            ### export logs to bot ###
            export_logs_to_bot(decoded_logs, path_export_logs)

            ### Add logs to the DB
            add_events_to_db(db_path, from_block, to_block, decoded_logs)
            

            from_block += BLOCK_TO_RETRIEVE
            to_block += BLOCK_TO_RETRIEVE
            
            if to_block - from_block > BLOCK_TO_RETRIEVE - 1:
                from_block = to_block - BLOCK_TO_RETRIEVE + 1

            sync_counter += 1

            if sync_counter > COUNT_BEFORE_RESYNC:
                sync_counter = 0
                current_block_number = w3[w3_main].eth.block_number
                to_block = current_block_number - BLOCK_BUFFER
                deviation = to_block - from_block - BLOCK_TO_RETRIEVE
                if deviation < 0:
                    from_block = current_block_number - BLOCK_BUFFER - BLOCK_TO_RETRIEVE + 1
                write_log(f"resync on newest block - deviation was {deviation} block(s)", 'logfile/logfile_indexingYAM.txt')

            if w3_main == 2:
                counter_backup += 1
                if counter_backup > 500:
                    write_log("counter_backup > 500: w3_main set to 0", 'logfile/logfile_indexingYAM.txt')
                    w3_main = 0
                    w3_backup = 1
                    counter_backup = 0

            execution_time = time.time() - start_time

            # Adjust sleep time accordingly (if the code took 3 seconds, sleep for 12 seconds)
            time_to_sleep = max(0, BLOCK_TO_RETRIEVE * 5 - execution_time)
            
            # Sleep for the adjusted time
            time.sleep(time_to_sleep)

            

        except KeyboardInterrupt:
            handle_keyboard_exception("index YAM stopped\n\n", 'logfile/logfile_indexingYAM.txt')
            
        except Exception as e:



            if unsuccessful_request_counter > 6:
                write_log(f"request to w3 [0] or [1] failed {unsuccessful_request_counter} times: w3_main set to 2", 'logfile/logfile_indexingYAM.txt')
                w3_main = 2
                w3_backup = 3

            if isinstance(e, ValueError):
                # Attempt to extract the error code from the exception message
                try:
                    error_data = eval(str(e))  # Convert the string representation of the error back to a dictionary
                    if error_data.get('code') == -32001:
                        write_log(f"Code: {error_data['code']}, Message: {error_data['message']}, w3_main = {w3_main}\n\tRetrying in {TIME_TO_WAIT_BEFORE_RETRY} secondes...", "logfile/logfile_indexingYAM.txt")
                        time.sleep(TIME_TO_WAIT_BEFORE_RETRY)
                except (SyntaxError, NameError, TypeError):
                    # If the eval fails, just proceed with handling the exception normally
                    handle_exception(e, 'Error: indexing YAM script failed', 'logfile/logfile_indexingYAM.txt', send_telegram_bool = True)

if __name__ == "__main__":
    main()