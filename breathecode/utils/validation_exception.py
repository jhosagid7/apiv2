import os
import logging

from rest_framework.exceptions import APIException

__all__ = ['ValidationException', 'APIException']

IS_TEST_ENV = os.getenv('ENV') == 'test'
logger = logging.getLogger(__name__)


class ValidationException(APIException):
    status_code = 400
    default_detail = 'There is an error in your request'
    default_code = 'client_error'
    slug = None

    def __init__(self, details, code=400, slug=None):
        self.status_code = code
        self.default_detail = details
        self.slug = slug
        self.detail = details

        if IS_TEST_ENV and slug:
            logger.error(f'Status {str(self.status_code)} - {slug}')
            super().__init__(slug)
        else:
            logger.error(f'Status {str(self.status_code)} - {details}')
            super().__init__(details)
