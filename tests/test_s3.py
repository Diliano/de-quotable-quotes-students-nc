from src.s3_tasks import write_file_to_s3, read_file_from_s3
import pytest
from moto import mock_aws
import os
import boto3


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def mock_s3(aws_credentials):
    with mock_aws():
        yield boto3.client("s3")


@pytest.fixture(scope="function")
def mock_bucket(mock_s3):
    mock_s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )


class TestWriteFileToS3:
    def test_writes_file_to_s3(self, mock_s3, mock_bucket):
        # Arrange
        test_filepath = "./tests/sonnet18.txt"
        test_bucket_name = "test-bucket"
        test_key = "sonnet18.txt"

        expected = "File uploaded to bucket: test-bucket, on key: sonnet18.txt"
        # Act
        result = write_file_to_s3(mock_s3, test_filepath, test_bucket_name, test_key)
        response = mock_s3.list_objects_v2(Bucket=test_bucket_name)
        # Act
        assert result == expected
        assert response["Contents"][0]["Key"] == test_key

    def test_returns_error_message_given_invalid_path_to_file(
        self, mock_s3, mock_bucket
    ):
        # Arrange
        test_filepath = "not_a_real_filepath"
        test_bucket_name = "test-bucket"
        test_key = "sonnet18.txt"
        # Act
        result = write_file_to_s3(mock_s3, test_filepath, test_bucket_name, test_key)
        # Assert
        assert result == "No file found with path_to_file: not_a_real_filepath"

    def test_returns_error_message_if_bucket_does_not_exist(self, mock_s3):
        # Arrange
        test_filepath = "./tests/sonnet18.txt"
        test_bucket_name = "test-bucket"
        test_key = "sonnet18.txt"
        # Act
        result = write_file_to_s3(mock_s3, test_filepath, test_bucket_name, test_key)
        # Assert
        assert (
            result
            == "Error: NoSuchBucket, Message: The specified bucket does not exist"
        )


class TestReadFileFromS3:
    def test_reads_file_from_s3(self, mock_s3, mock_bucket):
        # Arrange
        test_bucket_name = "test-bucket"
        test_key = "test.txt"
        test_content = b"This is unique content"
        test_destination = "./tests/test_read.txt"

        mock_s3.put_object(Bucket=test_bucket_name, Key=test_key, Body=test_content)
        # Act
        result = read_file_from_s3(
            mock_s3, test_bucket_name, test_key, test_destination
        )
        # Assert
        assert result == f"File saved to {test_destination}"

        with open(test_destination, "rb") as f:
            content = f.read()
        assert content == test_content

    def test_returns_error_message_given_invalid_bucket(self, mock_s3):
        # Arrange
        test_bucket_name = "not-a-real-bucket"
        test_key = "test.txt"
        test_destination = "./tests/test_read.txt"
        # Act
        result = read_file_from_s3(
            mock_s3, test_bucket_name, test_key, test_destination
        )
        # Assert
        assert (
            result
            == "Error: NoSuchBucket, Message: The specified bucket does not exist"
        )

    def test_returns_error_message_given_invalid_key(self, mock_s3, mock_bucket):
        # Arrange
        test_bucket_name = "test-bucket"
        test_key = "not_a_real_file.txt"
        test_destination = "./tests/test_read.txt"
        # Act
        result = read_file_from_s3(
            mock_s3, test_bucket_name, test_key, test_destination
        )
        # Assert
        assert result == "Error: NoSuchKey, Message: The specified key does not exist."

    def test_returns_error_message_given_invalid_destination(
        self, mock_s3, mock_bucket
    ):
        # Arrange
        test_bucket_name = "test-bucket"
        test_key = "test.txt"
        test_content = b"This is unique content"
        test_destination = "/not-a-real-folder/not_a_real_file.txt"

        mock_s3.put_object(Bucket=test_bucket_name, Key=test_key, Body=test_content)
        # Act
        result = read_file_from_s3(
            mock_s3, test_bucket_name, test_key, test_destination
        )
        # Assert
        assert result == f"Invalid destination: {test_destination}"
