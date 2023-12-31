import boto3
s3 = boto3.resource('s3', region_name='ap-southeast-2')
import base64

import os
from dotenv import load_dotenv
load_dotenv()

class AWSKMS:
    def __init__(self):
        self.kms = boto3.client('kms')
        self.key_id = os.getenv('AWS_KMS_KEY_ID')

    def sign_transaction(self, transaction_data):
        response = self.kms.sign(
            KeyId=self.key_id,
            Message=transaction_data,
            MessageType='RAW',
            SigningAlgorithm='ECDSA_SHA_256'
        )

        # Convert the signature to base64
        signature = base64.b64encode(response['Signature'])
        return signature
    
    def verify_signature(self, transaction_data, signature):
        response = self.kms.verify(
            KeyId=self.key_id,
            Message=transaction_data,
            MessageType='RAW',
            Signature=base64.b64decode(signature),
            SigningAlgorithm='ECDSA_SHA_256'
        )

        return response['SignatureValid']


