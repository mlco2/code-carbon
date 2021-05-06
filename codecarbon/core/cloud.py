# -*- coding: utf-8 -*-

# Copyright (C) 2020 [COMET-ML]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from logging import getLogger
from typing import Any, Dict, Optional

import requests

logger = getLogger("codecarbon")


def postprocess_gcp_cloud_metadata(cloud_metadata):
    # type: (Dict[str, Any]) -> Dict[str, Any]

    # Attributes contains custom metadata and also contains Kubernetes config,
    # startup script and secrets, filter it out
    if "attributes" in cloud_metadata:
        del cloud_metadata["attributes"]

    return cloud_metadata


CLOUD_METADATA_MAPPING = {
    "AWS": {
        "url": "http://169.254.169.254/latest/dynamic/instance-identity/document",
        "headers": {},
    },
    "Azure": {
        "url": "http://169.254.169.254/metadata/instance?api-version=2019-08-15",
        "headers": {"Metadata": "true"},
    },
    "GCP": {
        "url": "http://169.254.169.254/computeMetadata/v1/instance/?recursive=true&alt=json",
        "headers": {"Metadata-Flavor": "Google"},
        "postprocess_function": postprocess_gcp_cloud_metadata,
    },
}


def get_env_cloud_details(timeout=1):
    # type: (int) -> Optional[Any]
    """
    >>> get_env_cloud_details()
    {'provider': 'AWS',
     'metadata': {'accountId': '26550917306',
        'architecture': 'x86_64',
        'availabilityZone': 'us-east-1b',
        'billingProducts': None,
        'devpayProductCodes': None,
        'marketplaceProductCodes': None,
        'imageId': 'ami-025ed45832b817a35',
        'instanceId': 'i-7c3e81fed58d8f7f7',
        'instanceType': 'g4dn.2xlarge',
        'kernelId': None,
        'pendingTime': '2020-01-23T20:44:53Z',
        'privateIp': '172.156.72.143',
        'ramdiskId': None,
        'region': 'us-east-1',
        'version': '2017-09-30'}}
    """
    for provider in CLOUD_METADATA_MAPPING.keys():
        try:
            params = CLOUD_METADATA_MAPPING[provider]
            response = requests.get(
                params["url"], headers=params["headers"], timeout=timeout
            )
            response.raise_for_status()
            response_data = response.json()

            postprocess_function = params.get("postprocess_function")
            if postprocess_function is not None:
                response_data = postprocess_function(response_data)

            return {"provider": provider, "metadata": response_data}
        except Exception as e:
            logger.debug(
                "Not running on %s, couldn't retrieving metadata: %r", provider, e
            )

    return None
