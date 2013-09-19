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

"""Tests the sample data."""

__author__ = 'Sean Lip'

import os
import re
import string

import feconf
from core.domain import obj_services
from core.domain import widget_domain
import test_utils
import utils


# Sentinel indicating that a value can take any type.
ANY_TYPE = 1


class DataUnitTest(test_utils.GenericTestBase):
    """Base class for testing data and extension files."""

    def verify_dict_keys_and_types(self, adict, dict_schema):
        """Checks the keys in adict, and that their values have the right types.

        Args:
          adict: the dictionary to test.
          dict_schema: list of 2-element tuples. The first element of each
            tuple is the key name and the second element is the value type.
        """
        for item in dict_schema:
            self.assertEqual(
                len(item), 2, msg='Schema %s is invalid.' % dict_schema)
            self.assertTrue(isinstance(item[0], str))
            if item[1] != ANY_TYPE:
                self.assertTrue(isinstance(item[1], type))

        TOP_LEVEL_KEYS = [item[0] for item in dict_schema]
        self.assertItemsEqual(
            TOP_LEVEL_KEYS, adict.keys(),
            msg='Dict %s should conform to schema %s.' % (adict, dict_schema))

        for item in dict_schema:
            if item[1] == ANY_TYPE:
                continue
            self.assertTrue(
                isinstance(adict[item[0]], item[1]),
                'Value \'%s\' for key \'%s\' is not of type %s in:\n\n %s' % (
                    adict[item[0]], item[0], item[1], adict))


class ExplorationDataUnitTests(DataUnitTest):
    """Tests that all the default explorations are valid."""

    def verify_is_valid_widget(self, widget_id):
        """Checks that a widget id is valid (i.e., its directory exists)."""
        widget_dir = os.path.join(feconf.INTERACTIVE_WIDGETS_DIR, widget_id)
        self.assertTrue(os.path.isdir(widget_dir))

    def verify_state_dict(self, state_dict, state_name_list):
        """Verifies a state dictionary."""
        STATE_DICT_SCHEMA = [
            ('name', basestring),
            ('content', list), ('param_changes', list), ('widget', dict)]
        self.verify_dict_keys_and_types(state_dict, STATE_DICT_SCHEMA)

        curr_state = state_dict['name']

        # TODO(sll): Change the following verification once we move 'content'
        # to become a typed object.
        CONTENT_ITEM_SCHEMA = [('type', basestring), ('value', basestring)]
        for content_item in state_dict['content']:
            self.verify_dict_keys_and_types(content_item, CONTENT_ITEM_SCHEMA)
            self.assertIn(content_item['type'], ['text', 'image', 'video'])

        PARAM_CHANGES_SCHEMA = [
            ('name', basestring), ('generator_id', basestring),
            ('customization_args', ANY_TYPE)]
        for param_change in state_dict['param_changes']:
            self.verify_dict_keys_and_types(param_change, PARAM_CHANGES_SCHEMA)
            # TODO(sll): Test that the elements of 'values' are of the correct
            # type.

        WIDGET_SCHEMA = [
            ('widget_id', basestring), ('customization_args', dict),
            ('handlers', list), ('sticky', bool)]
        self.verify_dict_keys_and_types(state_dict['widget'], WIDGET_SCHEMA)

        for handler in state_dict['widget']['handlers']:
            HANDLER_SCHEMA = [('name', basestring), ('rule_specs', list)]
            self.verify_dict_keys_and_types(handler, HANDLER_SCHEMA)

            # Check that the list of rule_specs is non-empty.
            self.assertTrue(handler['rule_specs'])

            for rule in handler['rule_specs']:
                RULE_SCHEMA = [
                    ('dest', basestring), ('feedback', list),
                    ('definition', dict), ('param_changes', list)
                ]
                self.verify_dict_keys_and_types(rule, RULE_SCHEMA)

                # Check that the destination is a valid one.
                if rule['dest'] != feconf.END_DEST:
                    self.assertIn(rule['dest'], state_name_list)

                # Check that there are no feedback-less self-loops.
                # TODO(sll): For multiple-choice questions in which the other
                # rules cover all cases, do not raise an error.
                self.assertFalse(
                    rule['dest'] == curr_state and not rule['feedback']
                    and not state_dict['widget']['sticky'],
                    msg='State "%s" has a self-loop with no feedback. This is '
                    'likely to frustrate the reader.' % curr_state)

                # TODO(sll): Does 'inputs' need any tests?
                # TODO(sll): Check that the name corresponds to a valid one
                # from the relevant exploration -- maybe. (Need to decide if
                # we allow initialization of parameters midway through states.)
                for param_change in state_dict['param_changes']:
                    self.verify_dict_keys_and_types(
                        param_change, PARAM_CHANGES_SCHEMA)
                    # TODO(sll): Test that the elements of 'values' are of the
                    # correct type.

                # TODO(sll): Add validation for the rule definition.

        for wp_name, wp_value in (
                state_dict['widget']['customization_args'].iteritems()):
            self.assertTrue(isinstance(wp_name, basestring))

            # Check that the parameter name is valid.
            try:
                widget = widget_domain.Registry.get_widget_by_id(
                    feconf.INTERACTIVE_PREFIX,
                    state_dict['widget']['widget_id']
                )
            except Exception as e:
                raise Exception(
                    '%s; widget id: %s' %
                    (e, state_dict['widget']['widget_id'])
                )
            widget_param_names = [wp.name for wp in widget.params]
            self.assertIn(
                wp_name, widget_param_names,
                msg='Parameter %s is not a valid parameter for widget %s' % (
                    wp_name, state_dict['widget']['widget_id']))

            # Get the object class used to normalize the value for this param.
            for wp in widget.params:
                if wp.name == wp_name:
                    obj_class = obj_services.get_object_class(wp.obj_type)
                    self.assertIsNotNone(obj_class)
                    break

            # Check that the parameter value has the correct type.
            # TODO(sll): Replace this with a method that generates the
            # parameter and tests it. This method needs to be able to
            # substitute parameters if necessary, or be able to ignore
            # those cases.
            # obj_class.normalize(wp_value)

    def get_state_ind_from_name(self, states_list, state_name):
        """Given a state name, returns its index in the state list."""
        for ind, state in enumerate(states_list):
            if state['name'] == state_name:
                return ind

    def verify_all_states_reachable(self, states_list):
        """Verifies that all states are reachable from the initial state."""
        # Stores state names.
        processed_queue = []
        curr_queue = [states_list[0]['name']]
        while curr_queue:
            curr_state = curr_queue[0]
            curr_queue = curr_queue[1:]

            if curr_state in processed_queue:
                continue

            processed_queue.append(curr_state)

            curr_state_ind = self.get_state_ind_from_name(
                states_list, curr_state)

            for handler in states_list[curr_state_ind]['widget']['handlers']:
                for rule in handler['rule_specs']:
                    dest_state = rule['dest']
                    if (dest_state not in curr_queue and
                            dest_state not in processed_queue and
                            dest_state != feconf.END_DEST):
                        curr_queue.append(dest_state)

        if len(states_list) != len(processed_queue):
            unseen_states = list(
                set([s['name'] for s in states_list]) - set(processed_queue))
            raise Exception('The following states are not reachable from the '
                            'initial state: %s' % ', '.join(unseen_states))

    def verify_no_dead_ends(self, states_list):
        """Verifies that the END state is reachable from all states."""
        # Stores state names.
        processed_queue = []
        curr_queue = [feconf.END_DEST]
        while curr_queue:
            curr_state = curr_queue[0]
            curr_queue = curr_queue[1:]

            if curr_state in processed_queue:
                continue

            if curr_state != feconf.END_DEST:
                processed_queue.append(curr_state)

            for ind, state in enumerate(states_list):
                state_name = state['name']
                if (state_name not in curr_queue
                        and state_name not in processed_queue):
                    state_widget = states_list[ind]['widget']
                    for handler in state_widget['handlers']:
                        for rule in handler['rule_specs']:
                            if rule['dest'] == curr_state:
                                curr_queue.append(state_name)
                                break

        if len(states_list) != len(processed_queue):
            dead_end_states = list(
                set([s['name'] for s in states_list]) - set(processed_queue))
            raise Exception('The END state is not reachable from the '
                            'following states: %s' %
                            ', '.join(dead_end_states))

    def verify_exploration_dict(self, exploration_dict):
        """Verifies an exploration dict."""
        EXPLORATION_SCHEMA = [
            ('param_specs', dict), ('states', list),
            ('default_skin', basestring), ('param_changes', list),
            ('schema_version', int)
        ]
        self.verify_dict_keys_and_types(exploration_dict, EXPLORATION_SCHEMA)

        # Each param spec value should be a dict of the form
        # {obj_type: [STRING]}.
        for param_key in exploration_dict['param_specs']:
            ps_value = exploration_dict['param_specs'][param_key]
            if len(ps_value) != 1 or ps_value.keys()[0] != 'obj_type':
                raise Exception('Invalid param_spec dict: %s' % ps_value)

            obj_class = obj_services.get_object_class(ps_value['obj_type'])
            self.assertIsNotNone(obj_class)

        # Verify there is at least one state.
        self.assertTrue(exploration_dict['states'])

        state_name_list = []
        for state_desc in exploration_dict['states']:
            state_name = state_desc['name']
            if state_name in state_name_list:
                raise Exception('Duplicate state name: %s' % state_name)
            state_name_list.append(state_name)

        for state_desc in exploration_dict['states']:
            self.verify_state_dict(state_desc, state_name_list)

        self.verify_all_states_reachable(exploration_dict['states'])
        self.verify_no_dead_ends(exploration_dict['states'])

    def verify_exploration_yaml(self, exploration_yaml):
        """Verifies an exploration YAML file."""
        exploration_dict = utils.dict_from_yaml(exploration_yaml)
        self.verify_exploration_dict(exploration_dict)

    def test_default_explorations_are_valid(self):
        """Test the default explorations."""
        exploration_files = os.listdir(
            os.path.join(feconf.SAMPLE_EXPLORATIONS_DIR))

        self.assertTrue(feconf.DEMO_EXPLORATIONS,
                        msg='There must be at least one demo exploration.')

        self.assertEqual(len(exploration_files), len(feconf.DEMO_EXPLORATIONS),
                         msg='Files in data/explorations do not match the '
                             'demo explorations specified in feconf.py.')

        for exploration_filename in exploration_files:
            filepath = os.path.join(
                feconf.SAMPLE_EXPLORATIONS_DIR, exploration_filename)
            self.assertTrue(
                os.path.isfile(filepath), msg='%s is not a file.' % filepath)
            self.assertTrue(exploration_filename.endswith('.yaml'))

            # Read the exploration dictionary from the yaml file.
            with open(filepath) as f:
                self.verify_exploration_yaml(f.read().decode('utf-8'))


class WidgetDataUnitTests(DataUnitTest):
    """Tests that all the default widgets are valid."""

    def is_camel_cased(self, name):
        """Check whether a name is in CamelCase."""
        return name and (name[0] in string.ascii_uppercase)

    def is_alphanumeric_string(self, string):
        """Check whether a string is alphanumeric."""
        return bool(re.compile("^[a-zA-Z0-9]+$").match(string))

    def test_default_widgets_are_valid(self):
        """Test the default widgets."""
        widget_domain.Registry.refresh()

        self.assertEqual(
            len(widget_domain.Registry.interactive_widgets),
            feconf.INTERACTIVE_WIDGET_COUNT
        )
        self.assertEqual(
            len(widget_domain.Registry.noninteractive_widgets),
            feconf.NONINTERACTIVE_WIDGET_COUNT
        )

        bindings = widget_domain.Registry.interactive_widgets

        widget_ids = os.listdir(os.path.join(feconf.INTERACTIVE_WIDGETS_DIR))
        # TODO(sll): These tests ought to include non-interactive widgets as
        # well.

        for widget_id in widget_ids:
            # Check that the widget_id name is valid.
            self.assertTrue(self.is_camel_cased(widget_id))

            # Check that the widget directory exists.
            widget_dir = os.path.join(
                feconf.INTERACTIVE_WIDGETS_DIR, widget_id)
            self.assertTrue(os.path.isdir(widget_dir))

            # In this directory there should only be a config.yaml file, an
            # html entry-point file, a response.html file, (optionally) a
            # directory named 'static', (optionally) a response_iframe.html
            # file and (optionally) a stats_response.html file.
            dir_contents = os.listdir(widget_dir)
            self.assertLessEqual(len(dir_contents), 6)

            optional_dirs_and_files_count = 0

            try:
                self.assertIn('static', dir_contents)
                static_dir = os.path.join(widget_dir, 'static')
                self.assertTrue(os.path.isdir(static_dir))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            try:
                self.assertTrue(os.path.isfile(
                    os.path.join(widget_dir, 'stats_response.html')))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            try:
                self.assertTrue(os.path.isfile(os.path.join(
                    widget_dir, 'response_iframe.html')))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            try:
                self.assertTrue(os.path.isfile(os.path.join(
                    widget_dir, '%s.pyc' % widget_id)))
                optional_dirs_and_files_count += 1
            except Exception:
                pass

            self.assertEqual(
                optional_dirs_and_files_count + 3, len(dir_contents),
                dir_contents
            )

            py_file = os.path.join(widget_dir, '%s.py' % widget_id)
            html_entry_point = os.path.join(widget_dir, '%s.html' % widget_id)
            response_template = os.path.join(widget_dir, 'response.html')

            self.assertTrue(os.path.isfile(py_file))
            self.assertTrue(os.path.isfile(html_entry_point))
            self.assertTrue(os.path.isfile(response_template))

            WIDGET_CONFIG_SCHEMA = [
                ('name', basestring), ('category', basestring),
                ('description', basestring), ('_handlers', list),
                ('_params', list)
            ]

            widget = bindings[widget_id]

            # Check that the specified widget id is the same as the class name.
            self.assertTrue(widget_id, widget.__class__.__name__)

            # Check that the configuration file contains the correct
            # top-level keys, and that these keys have the correct types.
            for item, item_type in WIDGET_CONFIG_SCHEMA:
                self.assertTrue(isinstance(
                    getattr(widget, item), item_type
                ))
                # The string attributes should be non-empty.
                if item_type == basestring:
                    self.assertTrue(getattr(widget, item))

            # Check that at least one handler exists.
            self.assertTrue(
                len(widget.handlers),
                msg='Widget %s has no handlers defined' % widget_id
            )

            for handler in widget._handlers:
                HANDLER_KEYS = ['name', 'input_type']
                self.assertItemsEqual(HANDLER_KEYS, handler.keys())
                self.assertTrue(isinstance(handler['name'], basestring))
                # TODO(sll): Check that the input_type is either None or a
                # typed object.

            # Check that all handler names are unique.
            names = [handler.name for handler in widget.handlers]
            self.assertEqual(
                len(set(names)),
                len(names),
                'Widget %s has duplicate handler names' % widget_id
            )

            for param in widget._params:
                PARAM_KEYS = ['name', 'description', 'generator', 'init_args',
                              'customization_args', 'obj_type']
                for p in param:
                    self.assertIn(p, PARAM_KEYS)

                self.assertTrue(isinstance(param['name'], basestring))
                self.assertTrue(self.is_alphanumeric_string(param['name']))
                self.assertTrue(isinstance(param['description'], basestring))

                # TODO(sll): Check that the generator is a subclass of
                # BaseValueGenerator.

                self.assertTrue(isinstance(param['init_args'], dict))
                self.assertTrue(isinstance(param['customization_args'], dict))
                self.assertTrue(isinstance(param['obj_type'], basestring))

                obj_class = obj_services.get_object_class(param['obj_type'])
                self.assertIsNotNone(obj_class)

            # Check that the default customization args result in
            # parameters with the correct types.
            for param in widget.params:
                widget._get_widget_param_instances({}, {})
