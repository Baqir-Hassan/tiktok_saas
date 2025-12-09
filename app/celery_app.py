# This file is now deprecated in favor of the root celery.py
# but we can keep it to avoid breaking existing imports for now.
# It should import the shared app instance.

from __future__ import absolute_import, unicode_literals
from ..celeryconfig import app as celery_app

__all__ = ('celery_app',)
