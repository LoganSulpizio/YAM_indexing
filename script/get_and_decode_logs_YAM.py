if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from script.Utilities.contract_data import contract_data
from script.Utilities.get_address_normalized import get_address_normalized
from script.Utilities.write_logs import write_log

topic_yam = {
    'OfferCreated' : '0x9fa2d733a579251ad3a2286bebb5db74c062332de37e4904aa156729c4b38a65',
    'OfferDeleted' : '0x88686b85d6f2c3ab9a04e4f15a22fcfa025ffd97226dcf0a67cdf682def55676',
    'OfferAccepted': '0x0fe687b89794caf9729d642df21576cbddc748b0c8c7a5e1ec39f3a46bd00410',
    'OfferUpdated' : '0xc26a0a1f023ef119f120b3d9843d9e77dc8f66bbc0ea91d48d6dd39b8e351178'
}

def get_log_YAM_https(w3, contract_address, from_block, to_block, is_backup_w3 = False):
    logs = w3.eth.get_logs({
        'address': contract_address,
        'fromBlock': from_block,
        'toBlock': to_block
    })
    if is_backup_w3 == False:
        write_log(f"{len(logs)} log(s) of YAM retrieved from block {from_block} to {to_block}", "logfile/logfile_indexingYAM.txt")
    #else:
        #write_log(f"{len(logs)} log(s) of YAM retrieved from block {from_block} to {to_block} (backup)", "logfile/logfile_indexingYAM.txt")
    #pprint(logs)
    return logs

def decode_logs_YAM(logs):
    
    decoded_logs = []
    for log in logs:
        if log['topics'][0].hex() == topic_yam['OfferCreated']:
            event = decode_log_OfferCreated(log)
        elif log['topics'][0].hex() == topic_yam['OfferDeleted']:
            event = decode_log_OfferDeleted(log)
        elif log['topics'][0].hex() == topic_yam['OfferAccepted']:
            event = decode_log_OfferAccepted(log)
        elif log['topics'][0].hex() == topic_yam['OfferUpdated']:
            event = decode_log_OfferUpdated(log)
        else:
            event = None
        decoded_logs.append(event)
    if len(decoded_logs) > 0:
        decoded_logs_unique = decoded_logs_unique = [dict(t) for t in {frozenset(d.items()) for d in decoded_logs if d is not None}] # Remove duplicates logs
    else: decoded_logs_unique = decoded_logs
    return decoded_logs_unique

def decode_log_OfferCreated(log):

    offerToken = get_address_normalized(log['topics'][1].hex())
    buyerToken = get_address_normalized(log['topics'][2].hex())
    offerId = hex_to_decimal(log['topics'][3].hex())
    topic = 'OfferCreated'
    
    
    # Remove the '0x' prefix
    hex_data = log['data'].hex()[2:]

    seller_address = get_address_normalized('0x' + hex_data[:64])
    buyer_address = get_address_normalized('0x' + hex_data[64:128])
    price = hex_to_decimal(hex_data[130:192])
    amount = hex_to_decimal(hex_data[193:])

    custom_data_log = {
        'seller': seller_address,
        'buyer': buyer_address,
        'price': price,
        'amount': amount,
        'offerToken': offerToken,
        'buyerToken': buyerToken,
        'offerId' : offerId,
        'topic': topic
        }
    
    custom_data_log.update(get_generic_data_logs(log))


    debug = False
    if debug:
        print(hex_data)
        print('-' * 20)
        print(hex_data[:64])
        print(get_address_normalized('0x' + hex_data[:64]))
        print('-' * 20)
        print(get_address_normalized('0x' + hex_data[65:129]))
        print('-' * 20)
        print(hex_data[130:192])
        print(int(hex_data[130:192],16))
        print('-' * 20)
        print(hex_data[193:])
        print(int(hex_data[193:],16))

    return custom_data_log

def decode_log_OfferAccepted(log):

    offerId = hex_to_decimal(log['topics'][1].hex())
    seller_address = get_address_normalized(log['topics'][2].hex())
    buyer_address = get_address_normalized(log['topics'][3].hex())
    topic = 'OfferAccepted'
    
    
    # Remove the '0x' prefix
    hex_data = log['data'].hex()[2:]

    offerToken  = get_address_normalized('0x' + hex_data[:64])
    buyerToken  = get_address_normalized('0x' + hex_data[64:128])
    price = hex_to_decimal(hex_data[129:192])
    amount = hex_to_decimal(hex_data[193:])

    custom_data_log = {
        'seller': seller_address,
        'buyer': buyer_address,
        'price': price,
        'amount': amount,
        'offerToken': offerToken,
        'buyerToken': buyerToken,
        'offerId' : offerId,
        'topic': topic
        }
    
    custom_data_log.update(get_generic_data_logs(log))

    return custom_data_log

def decode_log_OfferUpdated (log):

    offerId = hex_to_decimal(log['topics'][1].hex())
    newPrice = hex_to_decimal(log['topics'][2].hex())
    newAmount = hex_to_decimal(log['topics'][3].hex())
    topic = 'OfferUpdated'
    
    # Remove the '0x' prefix
    hex_data = log['data'].hex()[2:]

    oldPrice  = hex_to_decimal(hex_data[:64])
    oldAmount   = hex_to_decimal(hex_data[64:])

    custom_data_log = {
        'oldPrice': oldPrice,
        'oldAmount': oldAmount,
        'newAmount': newAmount,
        'newPrice': newPrice,
        'offerId' : offerId,
        'topic': topic
        }

    custom_data_log.update(get_generic_data_logs(log))

    return custom_data_log

def decode_log_OfferDeleted(log):

    offerId = hex_to_decimal(log['topics'][1].hex())
    topic = 'OfferDeleted'

    custom_data_log = {
        'offerId' : offerId,
        'topic': topic
        }
    
    custom_data_log.update(get_generic_data_logs(log))

    return custom_data_log

def get_generic_data_logs(log):
    
    transactionHash = log['transactionHash'].hex()
    logIndex = log['logIndex']
    blockNumber = log['blockNumber']

    return {
        'transactionHash': transactionHash,
        'logIndex': logIndex,
        'blockNumber': blockNumber
        }

def hex_to_decimal(hex_str):
    return int(hex_str, 16)


### Test case ###
if __name__ == "__main__":
    from web3 import Web3
    from pprint import pprint
    w3 = Web3(Web3.HTTPProvider('https://go.getblock.io/a3dacad4a2e542aca148ed133b3a76b8'))
    #w3 = Web3(Web3.HTTPProvider('https://lb.nodies.app/v1/028d151f22f34f1f8e5137a928f0ee96'))
    #w3 = Web3(Web3.HTTPProvider('https://gnosis-mainnet.blastapi.io/9330add1-83d0-4f95-b445-326506a5d029'))
    #w3 = Web3(Web3.HTTPProvider('https://nd-684-905-991.p2pify.com/3aa16c5117029835a16cdd2534cfe4a9'))
    contract_address = contract_data['YAM']['address']  # Replace with your contract address
    from_block = 35526892  # You can specify the starting block number
    to_block = 35526909  # 'latest' to get up to the most recent block
    logs = get_log_YAM_https(w3, contract_address, from_block, to_block)
    #logs2 = get_log_YAM_https(w3, contract_address, from_block, to_block)
    decoded_logs = decode_logs_YAM(logs)
    pprint(decoded_logs)

