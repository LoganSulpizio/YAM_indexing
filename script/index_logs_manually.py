import os
import traceback
import time
import sys
from requests.exceptions import HTTPError
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from script.Utilities.write_logs import write_log
from script.Utilities.contract_data import contract_data
from script.get_and_decode_logs_YAM import get_log_YAM_https, decode_logs_YAM
from script.add_event_to_db import add_events_to_db


def index_manually(w3, contract_address, from_block, to_block_end, blocks_per_request, db_path):

    from_block_initial = from_block

    while True:

        to_block = from_block + blocks_per_request - 1

        try:

            logs = get_log_YAM_https(w3, contract_data['YAM']['address'], from_block, to_block)
            decoded_logs = decode_logs_YAM(logs)
            decoded_logs = sorted(decoded_logs, key=lambda x: x['blockNumber'])
            add_events_to_db(db_path, from_block, to_block, decoded_logs, write_timestamp = False)

            from_block += blocks_per_request
            to_block += blocks_per_request

            if to_block > to_block_end:
                log_message = f"{to_block - blocks_per_request - from_block_initial + 1} blocks retrieved: from block {from_block_initial} to block {to_block - blocks_per_request} ({round((to_block - blocks_per_request - from_block_initial + 1)*5/86400, 1)} days)"
                write_log(log_message, 'logfile/logfile_indexingYAM.txt')
                if __name__ == "__main__":
                    print(log_message)
                break

            time.sleep(0.022)

        except HTTPError as e:
            if e.response.status_code == 503:
                write_log("Service unavailable. Retrying in 5 seconds...", 'logfile/logfile_indexingYAM.txt')
                time.sleep(5)
                continue  # Retry the loop
            else:
                raise  # Re-raise the exception if it's not a 503 error    

        except KeyboardInterrupt:
            print(" Execution interrupted")
            write_log("index YAM stopped\n\n", 'logfile/logfile_indexingYAM.txt')
            sys.exit(0)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb = traceback.extract_tb(exc_tb)
            relevant_tb = [frame for frame in tb if frame.filename == __file__]
            
            if relevant_tb:
                filename, lineno, funcname, text = relevant_tb[-1]
            else:
                filename, lineno, funcname, text = tb[-1]
            
            error_message = 'Error: indexing YAM script failed:\n{}\nLine number: {}\n{}'.format(e, lineno, text)
            write_log(traceback.format_exc(), 'logfile/logfile_indexingYAM.txt')
            raise e

if __name__ == "__main__":
    from web3 import Web3
    import json
    #w3 = Web3(Web3.HTTPProvider('https://gnosis-mainnet.blastapi.io/9330add1-83d0-4f95-b445-326506a5d029'))
    w3 = Web3(Web3.HTTPProvider('https://go.getblock.io/a3dacad4a2e542aca148ed133b3a76b8'))
    contract_address = contract_data['YAM']['address'] 
    
    from_block = 36747958
    to_block_end = 36747966
    blocks_per_request = 5

    #from_block = 36676377
    #to_block_end = 36676377
    #blocks_per_request = 1

    # today = 36 679 854
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    db_path = config['db_path']
    index_manually(w3, contract_address, from_block, to_block_end, blocks_per_request, db_path)


'''
23/10/2024 13h48
from_block = 34445329
to_block_end = 34455329
blocks_per_request = 50

23/10/2024 13h56
from_block = 34455330
to_block_end = 34485330
blocks_per_request = 50

'''