#
# Copyright 2018-2019 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import os
import re
import shutil
import sys
import traceback

from ruamel.yaml import YAML


def print_banner(message):
    print('# --------------------------------------------------------'
          '---------------------------------')
    print('# {}'.format(message))
    print('# --------------------------------------------------------'
          '---------------------------------')


def capture_input(prompt, required=False, default=None):
    if default:
        prompt = '{} [{}]: '.format(prompt, default)
        required = False
    else:
        prompt = '{}: '.format(prompt)

    val = None
    if required:
        while not val:
            val = input(prompt).strip()
    else:
        val = input(prompt).strip()
        if not val:
            val = default

    return val


def select_from_choices(prompt, choices):
    assert len(choices) > 0
    print('{}:'.format(prompt))
    counter = 0
    for c in choices:
        print(' {}. {}'.format(counter + 1, c['name']))
        counter += 1

    if counter == 1:
        prompt = ' Pick one [1]: '
    else:
        prompt = ' Pick one: '
    val = None
    while not val:
        val = input(prompt).strip() or ''
        if not val and counter == 1:
            val = 1
        elif not val.isnumeric() or int(val) < 1 or int(val) > counter:
            print('  Enter a number between {} and {}'
                  .format(1, counter))
            val = None
    return choices[int(val) - 1]['value']


# ---------------------------------------
# Read config file
# ---------------------------------------
u_config_file = 'install_training_skeleton.json'
try:
    with open(u_config_file, 'r') as file:
        u_config = json.load(file)
    # sanity check
    assert u_config.get('supported_frameworks') is not None and \
        isinstance(u_config['supported_frameworks'], list)
except FileNotFoundError:
    print('Error. Could not find configuration file "{}".'
          .format(u_config_file))
    sys.exit(1)
except Exception as ex:
    print('Error. Could not load configuration file "{}".'
          .format(u_config_file))
    print(' Exception type: {}'.format(type(ex)))
    print(' Exception: {}'.format(ex))
    sys.exit(1)


# ---------------------------------------
# Prompt for destination directory
# ---------------------------------------
print_banner('MAX model training skeleton installation program.')
print('Please review the instructions in '
      'https://github.com/IBM/MAX-Training-Skeleton/')
print('Make sure you have cloned the MAX model repository before proceeding.')
invalid_dest = True
while invalid_dest:
    base_dest_dir = input('Enter the cloned model directory: ')
    if os.path.isdir(base_dest_dir):
        invalid_dest = False
    else:
        print(' Error. You must enter an existing directory name.')

dest_dir = os.path.join(base_dest_dir, 'training')

# ---------------------------------------
# Terminate if the destination already contains a training directory
# ---------------------------------------

if os.path.exists(dest_dir):
    if os.path.isdir(dest_dir):
        print('Error. Training directory already exists in "{}"'
              .format(base_dest_dir))
        print('To re-run the installation script remove "{}".'
              .format(dest_dir))
    else:
        print('Error. The destination exists "{}" but is not a directory'
              .format(dest_dir))
    sys.exit(1)

# ---------------------------------------
# Create training directory
# ---------------------------------------

try:
    print_banner('Creating training directory "{}" ...'
                 .format(dest_dir))
    os.makedirs(dest_dir)
except OSError as ose:
    print('Error. Could not create "{}": {}'
          .format(dest_dir, ose))
    sys.exit(1)

# ---------------------------------------
# Copy skeleton files
# ---------------------------------------

try:
    print_banner('Copying skeleton files to "{}" ...'
                 .format(dest_dir))

    def deep_copy(source, target):
        """Copies recursively all files from source to destination
        """
        names = os.listdir(source)
        os.makedirs(target, exist_ok=True)
        for name in names:
            src_name = os.path.join(source, name)
            tgt_name = os.path.join(target, name)
            if os.path.isdir(src_name):
                # source is a directory
                deep_copy(src_name, tgt_name)
            else:
                # source is a file
                print(' Copying "{}" to "{}" ...'
                      .format(src_name, tgt_name))
                shutil.copy2(src_name, tgt_name)

    # copy files recursively
    deep_copy('skeleton',
              dest_dir)

    # create the sample data data directory
    os.mkdir(os.path.join(dest_dir, 'sample_training_data', 'data'))

except Exception as ex:
    print('Error copying files: {}'.format(ex))
    sys.exit(1)

# ---------------------------------------
# Rename the configuration file in the destination directory
# ---------------------------------------

print_banner('Creating configuration file ...')

model_name = os.path.basename(base_dest_dir)

template_file = os.path.join(dest_dir, 'max-model-training-config.yaml')
if not os.path.isfile(template_file):
    print('Error. Template configuration file "{}" was not found.'
          .format(template_file))
    sys.exit(1)

# ---------------------------------------
# Customize the configuration file in the destination directory
# ---------------------------------------

print('Customizing configuration file ...')

try:
    yaml = YAML(typ='rt')
    yaml.default_flow_style = False
    yaml.preserve_qotes = True

    # load and parse config file
    with open(template_file, 'r') as file:
        conf = yaml.load(file)

    if conf is None or not isinstance(conf, dict):
        print('Error. The configuration file appears to be invalid.')
        print(conf)
        sys.exit(1)

    # required; model name
    conf['name'] = capture_input('Model name',
                                 required=False,
                                 default=model_name.replace('-', ' '))

    # required; model identifier
    conf['model_identifier'] = \
        capture_input('Model identifier',
                      required=False,
                      default=conf['name'].lower().replace(' ', '-'))

    # try to 'guess'the model description by peeking at
    # the model's config.py file (if one exists)
    model_description = None
    if os.path.isfile(os.path.join(base_dest_dir, 'config.py')):
        with open(os.path.join(base_dest_dir, 'config.py')) as model_config_py:
            prog = re.compile(r"\s*API_DESC\s*=\s*['\"]([^'\"]+)['\"]")
            for line in model_config_py:
                m = prog.match(line)
                if m:
                    model_description = m.group(1)
                    break

    # required; model description
    if model_description:
        conf['description'] = capture_input('Model description',
                                            default=model_description)
    else:
        conf['description'] = capture_input('Model description',
                                            required=True)

    # required; DL framework
    choices = []
    for supported_framework in u_config['supported_frameworks']:
        choices.append({
            'name': supported_framework['name'],
            'value': supported_framework['name']
        })

    fw = select_from_choices('Deep learning framework', choices)

    selected_framework = \
        next(framework for framework in u_config['supported_frameworks']
             if framework['name'] == fw)

    # required; DL framework identifier (as defined in WML)
    conf['framework']['name'] = selected_framework['id']

    # required; DL framework version
    conf['framework']['version'] = selected_framework['version']

    # required; DL serialization format
    choices = []
    for mp in selected_framework['model_path']:
        choices.append({
            'name': mp['name'],
            'value': mp['value']
        })
    for p in conf['process']:
        if p['name'] == 'training_process':
            p['params']['trained_model_path'] = \
                select_from_choices(
                    '{} model serialization format'
                    .format(fw),
                    choices)
            break

    # optional; key name prefix for training data
    conf['train']['data_source']['training_data']['path'] = \
        capture_input('Training data key name prefix', required=False)

    # save customized template
    customized_config_file = os.path.join(dest_dir,
                                          '{}-training-config.yaml'.format(
                                            conf['model_identifier']))

    print('Saving customized configuration file "{}"...'
          .format(customized_config_file))

    # save customized configuration file
    with open(customized_config_file, 'w') as file:
        yaml.dump(conf, file)
    # remove template
    os.remove(template_file)

except Exception:
    print('Error updating training configuration file {}:'
          .format(customized_config_file))
    traceback.print_ex()
    sys.exit(1)

try:
    # update .dockerignore
    print_banner('Updating .dockerignore ...')
    path_to_dockerignore = os.path.join(base_dest_dir, '.dockerignore')
    # identifies the required .dockerignore entries
    watchlist = [
                 {
                  'expr': re.compile(r"^training/?"),
                  'set': 'training/'}
                ]
    if os.path.isfile(path_to_dockerignore):
        file_content = None
        new_entries = []
        with open(path_to_dockerignore) as source:
            file_content = source.readlines()
            for element in watchlist:
                prog = element['expr']
                found = False
                for line in file_content:
                    m = prog.match(line)
                    if m:
                        found = True
                        break
                if not found:
                    new_entries.append(element['set'])

        if len(new_entries) > 0:
            print('Adding {} entries to .dockerignore'
                  .format(len(new_entries)))
            with open(path_to_dockerignore, 'w') as target:
                for entry in new_entries:
                    target.write('{}\n'.format(entry))
                target.writelines(file_content)

    # update .gitignore
    print_banner('Updating .gitignore ...')
    path_to_gitignore = os.path.join(base_dest_dir, '.gitignore')
    # identifies the required .gitignore entries
    watchlist = [
                 {
                  'expr': re.compile(r"^training/training_output/?"),
                  'set': 'training/training_output/'
                 },
                 {
                  'expr': re.compile(r"\*-model-building-code.zip"),
                  'set': '*-model-building-code.zip'
                 }
                ]
    if os.path.isfile(path_to_gitignore):
        file_content = None
        new_entries = []
        with open(path_to_gitignore) as source:
            file_content = source.readlines()
            for element in watchlist:
                prog = element['expr']
                found = False
                for line in file_content:
                    m = prog.match(line)
                    if m:
                        found = True
                        break
                if not found:
                    new_entries.append(element['set'])

        if len(new_entries) > 0:
            print('Adding {} entries to .gitignore'
                  .format(len(new_entries)))
            with open(path_to_gitignore, 'w') as target:
                for entry in new_entries:
                    target.write('{}\n'.format(entry))
                target.writelines(file_content)

except Exception:
    print('Error updating .dockerignore or .gitignore:')
    traceback.print_ex()
    sys.exit(1)

# ---------------------------------------
# Customize the README file in the destination directory
# Replace the mustache {{replace-me}} placeholders
# with the information the user provided
# ---------------------------------------
print('Customizing training README.md file ...')

try:

    readme_file = os.path.join(dest_dir, 'README.md')

    with open(readme_file, 'r') as r:
        readme_content = r.read()

    # each key maps to one or more placeholder
    # in the README.md template file
    placeholders = {
        'MAX-model-name': model_name,
        'lowercase-max-model-name': conf['model_identifier']
    }

    for placeholder in placeholders.keys():
        readme_content = \
            readme_content.replace('{{' + placeholder + '}}',
                                   placeholders[placeholder])

    with open(readme_file, 'w') as r:
        r.write(readme_content)

except Exception:
    print('Error updating {}:'.format(readme_file))
    traceback.print_ex()
    sys.exit(1)

print('The customized skeleton was saved in "{}".'
      .format(dest_dir))

print('To continue customization follow the instructions in '
      'https://github.com/IBM/MAX-Training-Skeleton/')
