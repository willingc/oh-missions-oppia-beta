# coding: utf-8
#
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

__author__ = 'Sean Lip'

import subprocess
import test_utils
import unittest


@unittest.skipIf(
    subprocess.call(['which', 'google-chrome', 'firefox']
                    ) == 1,
    'Firefox and/or Chrome binaries not found.'
)
class JavaScriptTests(test_utils.GenericTestBase):

    TAGS = [test_utils.TestTags.SLOW_TEST]

    def test_with_karma(self):
        return_code = subprocess.call([
            '../tools/node-0.10.1/bin/karma', 'start',
            'core/tests/karma.conf.js'])
        self.assertEqual(return_code, 0)
