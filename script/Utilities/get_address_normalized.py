from web3 import Web3

def get_address_normalized(hex_string: str):
    # Ensure the input string starts with '0x'
    if not hex_string.startswith('0x'):
        raise ValueError("Hex string must start with '0x'")
    
    # Step 1: Remove leading zeros after '0x'
    trimmed_hex = '0x' + hex_string[26:]  # Slice off the leading zeros

    # Step 2: Convert to checksummed address
    if trimmed_hex != '0x0000000000000000000000000000000000000000':
        checksummed_address = Web3.to_checksum_address(trimmed_hex)
    else: checksummed_address = trimmed_hex
    
    return checksummed_address


if __name__ == "__main__":
    # Example usage:
    hex_string = '0x000000000000000000000000a71d95d9c240eeeb12aebd2b64306bc18dc813e7'
    #hex_string = '0x' + ('0' * 64 )
    normalized_address = get_address_normalized(hex_string)
    print(normalized_address)