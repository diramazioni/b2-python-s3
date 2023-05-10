# Backblaze B2 Quick Start - Using Python with the Backblaze S3 Compatible API 

clone the repo and install requirements
```python
!git clone https://github.com/diramazioni/b2-python-s3 b2
%cd b2
!pip install -r requirements.txt
```

**edit/copy your .env file in b2 and verify it exists**
```python
%cd /content/b2
!cat .env
```
Import and instanciate
```python
from b2 import B2 
b2 = B2()
```
list_buckets
```python
b2.list_buckets()
```
work on this Bucket
```python
BUCKET_NAME = "test_bu-01"
```
Upload a file
```python
path =  os.path.abspath("README.md") #os.getcwd()
b2.upload_file(BUCKET_NAME, path)
```
download a file
```python
b2.download_file(BUCKET_NAME, "README.md")
```
create a folder
```python
b2.create_folder(BUCKET_NAME, "fold1")
b2.list_object_keys(BUCKET_NAME)
```
delete all versions of files
```python
b2.delete_files_all_versions(BUCKET_NAME, ['README.md'])
```
simply delete a file
```python
b2.delete_files(BUCKET_NAME, ['README.md'])
```
Create and delete a Bucket
```python
NEW="AAAAAA123"
b2.create_bucket(NEW)
b2.list_buckets()
b2.delete_bucket(NEW)
b2.list_buckets()
```
