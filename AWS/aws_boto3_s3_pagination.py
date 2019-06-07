'''
Experiments with a versioned S3 bucket to see if all updates for a given key are grouped together
when paginating.

Created on 7 Jun 2019

@author: si
'''
import boto3

IAM_ACCESS_ID='xxxxxxxxxxxxx'
IAM_ACCESS_KEY='xxxxxxxxxxxxxx'
BUCKET='my-bucket-xxa'
TEST_FILE = 'my_test_file_{}'

s3 = boto3.client('s3',
                  region_name='eu-west-1',
                  aws_access_key_id=IAM_ACCESS_ID,
                  aws_secret_access_key=IAM_ACCESS_KEY,)


def add_some_files(s3):
    for i in range(20):
        d = {   'Bucket': BUCKET,
                'Body': 'hello world',
                'Key': TEST_FILE.format(i)
            }
        s3.put_object(**d)

def create_versions(s3):
    "updates and deletes for file 3."

    for update_id in range(3):
        s3.put_object(Bucket=BUCKET,
                      Key=TEST_FILE.format(3),
                      Body=f'hello world {update_id}',
                      )

    s3.delete_object(Bucket=BUCKET,
                     Key=TEST_FILE.format(3)
                     )

    for update_id in range(3, 6):
        s3.put_object(Bucket=BUCKET,
                      Key=TEST_FILE.format(3),
                      Body=f'hello world {update_id}',
                      )

    s3.delete_object(Bucket=BUCKET,
                     Key=TEST_FILE.format(3)
                     )


# Run these two functions to initialise the bucket
# add_some_files(s3)
# create_versions(s3)

def list_files(client, page_size=10):
    paginator = client.get_paginator('list_object_versions')
    page_iterator = paginator.paginate(
        Bucket=BUCKET,
        PaginationConfig={'PageSize': page_size}
    )
    files_found = []
    page_number = -1
    for page in page_iterator:
        page_number += 1

        versions = page['Versions']
        delete_markers = page.get('DeleteMarkers', [])

        for d in delete_markers:
            files_found.append(f'Page {page_number} '+d['Key']+' (deleted)')

        for v in versions:
            files_found.append(f'Page {page_number} '+v['Key'])

    for f in files_found:
        print(f)

    print(len(files_found))

list_files(s3)
