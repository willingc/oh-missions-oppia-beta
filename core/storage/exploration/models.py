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

"""Dummy model file to keep django happy."""

__author__ = 'Tarashish Mishra'

from core.storage.exploration import django_models

StateModel = django_models.StateModel
ExplorationModel = django_models.ExplorationModel
ExplorationSnapshotModel = django_models.ExplorationSnapshotModel
ExplorationSnapshotContentModel = django_models.ExplorationSnapshotContentModel
