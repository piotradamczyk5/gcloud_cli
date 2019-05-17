# -*- coding: utf-8 -*- #
# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""e2e tests for ml local predict command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import subprocess

from googlecloudsdk.core.util import files
from tests.lib import parameterized
from tests.lib import sdk_test_base
from tests.lib import test_case
from tests.lib.surface.ml_engine import base


def _VerifyTensorflow():
  python_executables = files.SearchForExecutableOnPath('python')
  if not python_executables:
    raise RuntimeError('No python executable available')
  python_executable = python_executables[0]
  command = [python_executable, '-c', 'import tensorflow']
  proc = subprocess.Popen(command,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.returncode:
    raise RuntimeError(
        'Could not verify Tensorflow install.\n'
        'Python location: {python}\n'
        'Command to test: {command}\n'
        '----------------stdout----------------\n'
        '{stdout}'
        '----------------stderr----------------'
        '{stderr}'.format(python=python_executable, command=command,
                          stdout=stdout, stderr=stderr))


def _VerifyScikitLearn():
  python_executables = files.SearchForExecutableOnPath('python')
  if not python_executables:
    raise RuntimeError('No python executable available')
  python_executable = python_executables[0]
  command = [python_executable, '-c', 'import sklearn']
  proc = subprocess.Popen(
      command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.returncode:
    raise RuntimeError('Could not verify Scikit-learn install.\n'
                       'Python location: {python}\n'
                       'Command to test: {command}\n'
                       '----------------stdout----------------\n'
                       '{stdout}'
                       '----------------stderr----------------'
                       '{stderr}'.format(
                           python=python_executable,
                           command=command,
                           stdout=stdout,
                           stderr=stderr))


def _VerifyXgboost():
  python_executables = files.SearchForExecutableOnPath('python')
  if not python_executables:
    raise RuntimeError('No python executable available')
  python_executable = python_executables[0]
  command = [python_executable, '-c', 'import xgboost']
  proc = subprocess.Popen(
      command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.returncode:
    raise RuntimeError('Could not verify XGBoost install.\n'
                       'Python location: {python}\n'
                       'Command to test: {command}\n'
                       '----------------stdout----------------\n'
                       '{stdout}'
                       '----------------stderr----------------'
                       '{stderr}'.format(
                           python=python_executable,
                           command=command,
                           stdout=stdout,
                           stderr=stderr))


try:
  _VerifyTensorflow()
except RuntimeError as err:
  tensorflow_available = False
  reason = 'Needs tensorflow installed: ' + str(err)
else:
  tensorflow_available = True
  reason = 'Needs tensorflow installed'
try:
  _VerifyScikitLearn()
except RuntimeError as err:
  sklearn_available = False
  reason = 'Needs scikit-learn installed: ' + str(err)
else:
  sklearn_available = True
  reason = 'Needs scikit-learn installed'
try:
  _VerifyXgboost()
except RuntimeError as err:
  xgboost_available = False
  reason = 'Needs XGBoost installed: ' + str(err)
else:
  xgboost_available = True
  reason = 'Needs XGBoost installed'


# If this test is skipped, we have very little effective coverage of this code
# path and it should be treated as a high-priority issue.
@sdk_test_base.Filters.RunOnlyInBundle
@test_case.Filters.RunOnlyIf(tensorflow_available, reason)
@parameterized.parameters('ml-engine', 'ai-platform')
class TensorflowPredictTest(base.MlGaPlatformTestBase):
  """e2e tests for ai-platform local predict command using tensorflow."""

  @property
  def model_path(self):
    return self.Resource('tests', 'e2e', 'surface', 'ai_platform', 'testdata',
                         'savedmodel')

  def testLocalPredict(self, module_name):
    json_instances = self.Resource('tests', 'e2e', 'surface', 'ai_platform',
                                   'testdata', 'predict_sample.tensor.json')

    results = self.Run('{} local predict '
                       '    --model-dir={} '
                       '    --json-instances={}'.format(
                           module_name, self.model_path, json_instances))

    # Prediction output should look something like the following:
    # {'predictions' : [{'prediction': 0, 'key': 0, scores: [0, 1, ...]}, ...]}
    self.AssertOutputMatches(r"""KEY PREDICTION SCORES
0 5 \[0\.0372[e0-9-]+, 0\.0005[e0-9-]+, 0\.0171[e0-9-]+, 0\.3897[e0-9-]+, 2\.2457[e0-9-]+, 0\.5273[e0-9-]+, 0\.0004[e0-9-]+, 0\.0043[e0-9-]+, 0\.0200[e0-9-]+, 0\.0030[e0-9-]+\]
1 0 \[0\.9942[e0-9-]+, 1\.8777[e0-9-]+, 7\.3985[e0-9-]+, 5\.8089[e0-9-]+, 4\.6430[e0-9-]+, 0\.0054[e0-9-]+, 1\.5826[e0-9-]+, 1\.3173[e0-9-]+, 0\.0002[e0-9-]+, 4\.1962[e0-9-]+\]
2 4 \[0\.0026[e0-9-]+, 0\.000740[e0-9-]+, 0\.011052[e0-9-]+, 0\.0334[e0-9-]+, 0\.6492[e0-9-]+, 0\.0116[e0-9-]+, 0\.0265[e0-9-]+, 0\.0175[e0-9-]+, 0\.0138[e0-9-]+, 0\.2332[e0-9-]+\]
3 1 \[1\.0442[e0-9-]+, 0\.9607[e0-9-]+, 0\.0071[e0-9-]+, 0\.0028[e0-9-]+, 0\.0002[e0-9-]+, 0\.0018[e0-9-]+, 0\.0003[e0-9-]+, 0\.0004[e0-9-]+, 0\.0260[e0-9-]+, 0\.0002[e0-9-]+\]
4 9 \[4\.2311[e0-9-]+, 0\.0002[e0-9-]+, 6\.5845[e0-9-]+, 0\.0001[e0-9-]+, 0\.1294[e0-9-]+, 0\.0011[e0-9-]+, 0\.0001[e0-9-]+, 0\.0168[e0-9-]+, 0\.0049[e0-9-]+, 0\.8470[e0-9-]+\]
5 2 \[0\.0033[e0-9-]+, 0\.0001[e0-9-]+, 0\.8451[e0-9-]+, 0\.0190[e0-9-]+, 0\.0002[e0-9-]+, 0\.0015[e0-9-]+, 0\.0005[e0-9-]+, 0\.0186[e0-9-]+, 0\.0233[e0-9-]+, 0\.0880[e0-9-]+\]
6 1 \[2\.8456[e0-9-]+, 0\.9884[e0-9-]+, 0\.0016[e0-9-]+, 0\.0070[e0-9-]+, 1\.1605[e0-9-]+, 0\.0004[e0-9-]+, 0\.0001[e0-9-]+, 0\.0001[e0-9-]+, 0\.0018[e0-9-]+, 0\.0003[e0-9-]+\]
7 3 \[8\.3056[e0-9-]+, 6\.9804[e0-9-]+, 0\.0020[e0-9-]+, 0\.9807[e0-9-]+, 1\.2836[e0-9-]+, 0\.0019[e0-9-]+, 1\.0807[e0-9-]+, 0\.0001[e0-9-]+, 0\.0137[e0-9-]+, 0\.0012[e0-9-]+\]
8 1 \[1\.9162[e0-9-]+, 0\.9807[e0-9-]+, 0\.0017[e0-9-]+, 0\.0066[e0-9-]+, 0\.0001[e0-9-]+, 0\.0039[e0-9-]+, 0\.0006[e0-9-]+, 0\.0007[e0-9-]+, 0\.0041[e0-9-]+, 0\.0010[e0-9-]+\]
9 4 \[0\.0002[e0-9-]+, 1\.8026[e0-9-]+, 0\.0002[e0-9-]+, 6\.4285[e0-9-]+, 0\.9642[e0-9-]+, 0\.0051[e0-9-]+, 0\.0157[e0-9-]+, 0\.0004[e0-9-]+, 0\.0049[e0-9-]+, 0\.0088[e0-9-]+\]
""", normalize_space=True)
    self.assertEqual(list(results.keys()), ['predictions'])
    predictions = results['predictions']
    self.assertEqual(len(predictions), 10)
    expected_keys = set(['prediction', 'key', 'scores'])
    for prediction in predictions:
      self.assertSetEqual(set(prediction.keys()), expected_keys)


# If this test is skipped, we have very little effective coverage of this code
# path and it should be treated as a high-priority issue.
@sdk_test_base.Filters.RunOnlyInBundle
@test_case.Filters.RunOnlyIf(sklearn_available, reason)
@parameterized.parameters('ml-engine', 'ai-platform')
class ScikitLearnPredictTest(base.MlGaPlatformTestBase):
  """e2e tests for ai-platform local predict command using scikit-learn."""

  @property
  def model_path(self):
    return self.Resource('tests', 'e2e', 'surface', 'ai_platform', 'testdata',
                         'scikit_learn_iris_model')

  def testLocalPredict(self, module_name):
    json_instances = self.Resource('tests', 'e2e', 'surface', 'ai_platform',
                                   'testdata', 'iris_model_input.json')

    results = self.Run('{} local predict '
                       '    --model-dir={} '
                       '    --framework=scikit-learn'
                       '    --json-instances={}'.format(
                           module_name, self.model_path, json_instances))

    # Prediction output should look something like the following:
    # {'predictions' : [2,2]}
    self.AssertOutputMatches('[2,2]')
    self.assertEqual(list(results.keys()), ['predictions'])
    predictions = results['predictions']
    self.assertEqual(len(predictions), 2)


# If this test is skipped, we have very little effective coverage of this code
# path and it should be treated as a high-priority issue.
@sdk_test_base.Filters.RunOnlyInBundle
@test_case.Filters.RunOnlyIf(xgboost_available, reason)
@parameterized.parameters('ml-engine', 'ai-platform')
class XgboostPredictTest(base.MlGaPlatformTestBase):
  """e2e tests for ai-platform local predict command using xgboost."""

  @property
  def model_path(self):
    return self.Resource('tests', 'e2e', 'surface', 'ai_platform', 'testdata',
                         'xgboost_iris_model')

  def testLocalPredict(self, module_name):
    json_instances = self.Resource('tests', 'e2e', 'surface', 'ai_platform',
                                   'testdata', 'iris_model_input.json')

    results = self.Run('{} local predict '
                       '    --model-dir={} '
                       '    --framework=xgboost'
                       '    --json-instances={}'.format(
                           module_name, self.model_path, json_instances))

    self.AssertOutputMatches(
        r"""\[\[0.989785[e0-9-]+, 0.005485[e0-9-]+, 0.004728[e0-9-]+\],
        \[0.989785[e0-9-]+, 0.005485[e0-9-]+, 0.004728[e0-9-]+\]\]""",
        normalize_space=' \t\v\n')
    self.assertEqual(list(results.keys()), ['predictions'])
    predictions = results['predictions']
    self.assertEqual(len(predictions), 2)


if __name__ == '__main__':
  test_case.main()