# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Service methods for typed instances."""

__author__ = 'Sean Lip'

from extensions.objects.models import objects


def get_object_class(cls_name):
    """Gets the object class based on the class name."""
    try:
        assert cls_name != 'BaseObject'

        object_class = getattr(objects, cls_name)
        assert object_class
    except Exception:
        raise TypeError('\'%s\' is not a valid typed object class.' % cls_name)

    return object_class
