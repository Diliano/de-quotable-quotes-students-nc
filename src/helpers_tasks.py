import random
from data.quotes import quote_list
from botocore.exceptions import ClientError


def get_quote():
    """Function mimicking a call to an external quotes API.

    Requests a random quote, retrieving both the author and the text of the
    quote.

    Returns:
      (On success) a tuple consisting of a HTTP status code and a dict
      containing the content, author and length of the quote as keys.
      (On failure) a tuple with a status code and a dict containing the
      status message.
    """
    try:
        quote = random.choice(quote_list)
        required = ["content", "author", "length"]
        return (200, {k: quote[k] for k in required})
    except Exception as e:
        formatted = {"status_message": f"Unexpected error: {e}"}
        return (500, formatted)


def get_parameter(ssm_client, parameter_name, **kwargs):
    """Gets a parameter from AWS Systems Manager Parameter Store.

    Finds the given parameter name in the Parameter store and returns the
    value.

    Args:
      ssm_client (boto3.client): the boto3 client to interact with the AWS API.
      parameter_name: the unique name of the parameter.
      (optional) kwargs

    Returns:
      A string with the required parameter value or an informative error
      message.

    """
    try:
        response = ssm_client.get_parameter(Name=parameter_name)
        return response["Parameter"]["Value"]
    except ClientError as error:
        raise error
