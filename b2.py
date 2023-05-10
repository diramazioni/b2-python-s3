#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv
import os


class B2:
    def __init__(self):
        if not os.path.exists('/.dockerenv'): 
            load_dotenv()
        self.endpoint = os.getenv("ENDPOINT_URL_YOUR_BUCKET")
        self.key_id = os.getenv("KEY_ID_YOUR_ACCOUNT")
        self.application_key = os.getenv("APPLICATION_KEY_YOUR_ACCOUNT")
        self.b2_resource = self.get_b2_resource(self.endpoint, self.key_id, self.application_key)
        self.b2_client = self.get_b2_client(self.endpoint, self.key_id, self.application_key)

    def copy_file(self, source_bucket, destination_bucket, source_key, destination_key):
        try:
            source = {
                'Bucket': source_bucket,
                'Key': source_key
            }
            self.b2_resource.Bucket(destination_bucket).copy(source, destination_key)
        except ClientError as ce:
            print('error', ce)

    def create_bucket(self, name, secure=False):
        try:
            self.b2_resource.create_bucket(Bucket=name)
            if secure:
                self.prevent_public_access(name)
        except ClientError as ce:
            print('error', ce)

    def delete_bucket(self, bucket):
        try:
            self.b2_resource.Bucket(bucket).delete()
        except ClientError as ce:
            print('error', ce)

    def delete_files(self, bucket, keys):
        objects = []
        for key in keys:
            objects.append({'Key': key})
        try:
            self.b2_resource.Bucket(bucket).delete_objects(Delete={'Objects': objects})
        except ClientError as ce:
            print('error', ce)

    def delete_files_all_versions(self, bucket, keys):
        objects = []
        for key in keys:
            objects.append({'Key': key})
        try:
            paginator = self.b2_client.get_paginator('list_object_versions')
            response_iterator = paginator.paginate(Bucket=bucket)
            for response in response_iterator:
                versions = response.get('Versions', [])
                versions.extend(response.get('DeleteMarkers', []))
                for version_id in [x['VersionId'] for x in versions if x['Key'] == key and x['VersionId'] != 'null']:
                    print('Deleting {} version {}'.format(key, version_id))
                    self.b2_client.delete_object(Bucket=bucket, Key=key, VersionId=version_id)
        except ClientError as ce:
            print('error', ce)
            
    def upload_file(self, bucket, file_path, b2path=None):
        directory, file = os.path.split(file_path)
        remote_path = b2path if b2path else file
        try:
            response = self.b2_resource.Bucket(bucket).upload_file(file_path, remote_path)
        except ClientError as ce:
            print('error', ce)
        return response
    
    def download_file(self, bucket, key_name, file_path=None):
        file_path = file_path if file_path else key_name
        directory, local_name = os.path.split(file_path)
        try:
            self.b2_resource.Bucket(bucket).download_file(key_name, file_path)
        except ClientError as ce:
            print('error', ce)

    def create_folder(self, bucket, folder_path):
        folder_path = folder_path.strip('/')
        try:
            response = self.b2_client.put_object(Bucket=bucket, Key=(folder_path + '/'))
        except ClientError as ce:
            print('error', ce)
        return response
    
    def get_object_presigned_url(self, bucket, key, expiration_seconds):
        try:
            response = self.b2_resource.meta.client.generate_presigned_url(
                ClientMethod='get_object',
                ExpiresIn=expiration_seconds,
                Params={
                    'Bucket': bucket,
                    'Key': key
                }
            )
            return response
        except ClientError as ce:
            print('error', ce)

    def list_buckets(self, raw_object=False):
        try:
            my_buckets_response = self.b2_client.list_buckets()
            print('\nBUCKETS')
            for bucket_object in my_buckets_response['Buckets']:
                print(bucket_object['Name'])
            if raw_object:
                print('\nFULL RAW RESPONSE:')
                print(my_buckets_response)
        except ClientError as ce:
            print('error', ce)

    def list_object_keys(self, bucket):
        try:
            response = self.b2_resource.Bucket(bucket).objects.all()           
            return_list = []
            for object in response:
                return_list.append(object.key)
            return return_list
        except ClientError as ce:
            print('error', ce)

    def list_objects_browsable_url(self, bucket, endpoint):
        try:
            bucket_object_keys = self.list_object_keys(bucket)
            return_list = []
            for key in bucket_object_keys:
                url = f"{endpoint}/{bucket}/{key}"
                return_list.append(url)
            return return_list
        except ClientError as ce:
            print('error', ce)

    def get_b2_client(self, endpoint, keyID, applicationKey):
        b2_client = boto3.client(
            service_name='s3',
            endpoint_url=endpoint,
            aws_access_key_id=keyID,
            aws_secret_access_key=applicationKey
        )
        return b2_client

    def get_b2_resource(self, endpoint, keyID, applicationKey):
        b2 = boto3.resource(
            service_name='s3',
            endpoint_url=endpoint,
            aws_access_key_id=keyID,
            aws_secret_access_key=applicationKey,
            config=Config(signature_version='s3v4')
        )
        return b2

    def prevent_public_access(self, bucket):
        try:
            self.b2_client.put_public_access_block(
                Bucket=bucket,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
        except ClientError as ce:
            print('error', ce)
