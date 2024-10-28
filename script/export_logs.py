import os
import json

def export_logs_to_bot(decoded_logs: list, export_path: str):
    for log in decoded_logs:

        if log['topic'] == 'OfferAccepted':

             # Create a filename using the transaction hash
             file_name = os.path.join(export_path, f"{log['transactionHash']}.json")
             
             # Write the log dictionary to a JSON file
             with open(file_name, 'w') as json_file:
                 json.dump(log, json_file, indent=4)
        



### Test case ###
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

    # Get the system drive dynamically
    system_drive = os.path.splitdrive(os.path.abspath(os.sep))[0]
    
    # Define the path components, with the first component being the root directory
    path_components = [
        os.sep,  # This adds the root directory ('\')
        'DeFi', 
        'TelegramBot', 
        'YAMSaleNotifyBot', 
        'transaction_queue'
    ]
    
    # Construct the path
    path = os.path.join(system_drive, *path_components)

    from web3 import Web3
    from pprint import pprint
    from Utilities.contract_data import contract_data
    from script.get_and_decode_logs_YAM  import get_log_YAM_https, decode_logs_YAM
    w3 = Web3(Web3.HTTPProvider('https://go.getblock.io/a3dacad4a2e542aca148ed133b3a76b8'))
    #w3 = Web3(Web3.HTTPProvider('https://gnosis-mainnet.blastapi.io/9330add1-83d0-4f95-b445-326506a5d029'))
    #w3 = Web3(Web3.HTTPProvider('https://nd-684-905-991.p2pify.com/3aa16c5117029835a16cdd2534cfe4a9'))
    contract_address = contract_data['YAM']['address']  # Replace with your contract address
    from_block = 35559000  # You can specify the starting block number
    to_block = 355589099  # 'latest' to get up to the most recent block
    logs = get_log_YAM_https(w3, contract_address, from_block, to_block)
    logs2 = get_log_YAM_https(w3, contract_address, from_block, to_block)
    decoded_logs = decode_logs_YAM(logs+logs2)
    #pprint(decoded_logs)
    export_logs_to_bot(decoded_logs, path)