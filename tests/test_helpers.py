import pytest
from unittest.mock import patch
from src.helpers_tasks import get_quote, get_parameter
from moto import mock_aws
import os
import boto3
from botocore.exceptions import ClientError


@pytest.fixture(scope="function")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def mock_ssm(aws_credentials):
    with mock_aws():
        yield boto3.client("ssm")


class TestGetQuote:
    """Tests the get_quote helper."""

    def test_get_quote_returns_status_and_formatted_dict(
        self, sample_quote_list, result_quote_1
    ):
        with patch("src.helpers_tasks.random.choice") as mock_choice:
            mock_choice.return_value = sample_quote_list[0]
            assert get_quote() == (200, result_quote_1)

    def test_get_quote_valid_url(self):
        status_code, _ = get_quote()
        assert status_code == 200

    def test_get_quote_error_response(self):
        with patch(
            "src.helpers_tasks.random.choice",
            side_effect=Exception("The requested resource could not be found"),
        ):
            status_code, response = get_quote()
            assert status_code == 500
            assert response == {
                "status_message": (
                    "Unexpected error: The requested resource could not be found"
                )
            }


class TestGetParameter:
    def test_gets_specified_parameter_value(self, mock_ssm):
        # Arrange
        mock_ssm.put_parameter(
            Name="test_param", Value="I am a unique test parameter", Type="String"
        )
        expected = "I am a unique test parameter"
        # Act
        result = get_parameter(mock_ssm, "test_param")
        # Assert
        assert result == expected

    def test_raises_error_given_invalid_param_name(self, mock_ssm):
        # Arrange
        mock_ssm.put_parameter(
            Name="test_param", Value="I am a unique test parameter", Type="String"
        )
        # Act + Assert
        with pytest.raises(ClientError) as excinfo:
            get_parameter(mock_ssm, "not_a_param")

        assert (
            str(excinfo.value)
            == "An error occurred (ParameterNotFound) when calling the GetParameter operation: Parameter not_a_param not found."
        )
