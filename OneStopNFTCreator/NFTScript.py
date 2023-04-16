import hashlib
import json

import algosdk
from algosdk.v2client import algod
from beaker import sandbox
from algosdk.transaction import AssetConfigTxn, AssetOptInTxn, AssetTransferTxn, wait_for_confirmation

def mintNFT(algod_client, creator_address, creator_private_key, asset_name, asset_unit_name):

    sp = algod_client.suggested_params()

    txn = AssetConfigTxn(
        sender=creator_address,
        sp=sp,
        default_frozen=False,
        unit_name=asset_unit_name,
        asset_name=asset_name,
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        url="ipfs://QmRP2bnvSSyvdqdRPLiDeQNWgv6MeDxCLCeFW8W5TqgYSx#arc3",
        total=1,
        decimals=0,
    )

    stxn = txn.sign(private_key=creator_private_key)

    txid = algod_client.send_transaction(stxn)

    results = wait_for_confirmation(algod_client, txid, 4)

    created_asset = results["asset-index"]

    return created_asset #your confirmed transaction's asset id should be returned instead


def transferNFT(algod_client, creator_address, creator_private_key, receiver_address, receiver_private_key, asset_id):
    sp = algod_client.suggested_params()

    optin_txn = AssetOptInTxn(
        sender=receiver_address, sp=sp, index=asset_id
    )
    
    signed_optin_txn = optin_txn.sign(receiver_private_key)
    txid = algod_client.send_transaction(signed_optin_txn)
    results = wait_for_confirmation(algod_client, txid, 4)

    sp = algod_client.suggested_params()

    # Create transfer transaction
    xfer_txn = AssetTransferTxn(
        sender=creator_address,
        sp=sp,
        receiver=receiver_address,
        amt=1,
        index=asset_id,
    )

    signed_xfer_txn = xfer_txn.sign(creator_private_key)
    txid = algod_client.send_transaction(signed_xfer_txn)
    results = wait_for_confirmation(algod_client, txid, 4)

    pass

if __name__ == "__main__":
    accounts = sandbox.kmd.get_accounts()
    sender = accounts[0]
    reciever = accounts[1]

    client = sandbox.get_algod_client()

    aid = mintNFT(client, sender.address, sender.private_key, "HackaCoin", "hc")
    transferNFT(client, sender.address, sender.private_key, reciever.address, reciever.private_key, aid)

    print(client.asset_info(aid))
    print(client.account_asset_info(reciever.address, aid))