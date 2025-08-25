import boto3
import json
import streamlit as st

# Connect to S3 using st.secrets
s3 = boto3.client(
    "s3",
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY"],
    aws_secret_access_key=st.secrets["AWS_SECRET_KEY"],
    region_name=st.secrets["AWS_REGION"]
)

# Bucket name from secrets
BUCKET = st.secrets["AWS_BUCKET"]

def read_json_from_s3(filename):
    """Download JSON from S3 (returns list/dict)."""
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=filename)
        return json.loads(obj["Body"].read())
    except s3.exceptions.NoSuchKey:
        return []  # Start fresh if file doesn't exist yet

def write_json_to_s3(filename, data):
    """Upload JSON to S3."""
    s3.put_object(
        Bucket=BUCKET,
        Key=filename,
        Body=json.dumps(data, indent=2)
    )

def append_to_json_in_s3(filename, new_entry):
    """Append new entry to JSON in S3."""
    data = read_json_from_s3(filename)
    data.append(new_entry)
    write_json_to_s3(filename, data)
