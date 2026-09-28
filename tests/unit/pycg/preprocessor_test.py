#
# Copyright (c) 2020 Vitalis Salis.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import ast
import os
import tempfile

from onecode.pycg.machinery.classes import ClassManager
from onecode.pycg.machinery.definitions import DefinitionManager
from onecode.pycg.machinery.imports import ImportManager
from onecode.pycg.machinery.modules import ModuleManager
from onecode.pycg.machinery.scopes import ScopeManager
from onecode.pycg.processing.preprocessor import PreProcessor
from tests.unit.pycg.base import TestBase


class PreprocessorTest(TestBase):
    def _make_preprocessor(self, code):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            fname = f.name

        im = ImportManager()
        sm = ScopeManager()
        dm = DefinitionManager()
        cm = ClassManager()
        mm = ModuleManager()
        pp = PreProcessor(fname, "mod", im, sm, dm, cm, mm, modules_analyzed=set())
        return pp, fname

    def test_get_fun_defaults_posonlyargs(self):
        code = "def eye(n_rows, n_cols=None, /): pass\n"
        pp, fname = self._make_preprocessor(code)
        try:
            node = ast.parse(code).body[0]
            defaults = pp._get_fun_defaults(node)
            self.assertIn("n_cols", defaults)
            self.assertEqual(defaults["n_cols"], [None])
        finally:
            os.unlink(fname)

    def test_get_fun_defaults_positional_or_keyword(self):
        code = "def f(a, b=1): pass\n"
        pp, fname = self._make_preprocessor(code)
        try:
            node = ast.parse(code).body[0]
            defaults = pp._get_fun_defaults(node)
            self.assertIn("b", defaults)
            self.assertEqual(defaults["b"], [1])
        finally:
            os.unlink(fname)
