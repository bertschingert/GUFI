#!/usr/bin/env @PYTHON_INTERPRETER@
# This file is part of GUFI, which is part of MarFS, which is released
# under the BSD license.
#
#
# Copyright (c) 2017, Los Alamos National Security (LANS), LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# From Los Alamos National Security, LLC:
# LA-CC-15-039
#
# Copyright (c) 2017, Los Alamos National Security, LLC All rights reserved.
# Copyright 2017. Los Alamos National Security, LLC. This software was produced
# under U.S. Government contract DE-AC52-06NA25396 for Los Alamos National
# Laboratory (LANL), which is operated by Los Alamos National Security, LLC for
# the U.S. Department of Energy. The U.S. Government has rights to use,
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR LOS
# ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
# modified to produce derivative works, such modified software should be
# clearly marked, so as not to confuse it with the version available from
# LANL.
#
# THIS SOFTWARE IS PROVIDED BY LOS ALAMOS NATIONAL SECURITY, LLC AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL LOS ALAMOS NATIONAL SECURITY, LLC OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.



import sqlite3
import unittest

from performance_pkg.hashdb import gufi, machine, raw_data, utils as hashdb

# test hashdb.get_config_with_con (instead of
# hashdb.get_config) to not have to create an
# actual file
class TestGetConfig(unittest.TestCase):
    GUFI_CMD   = 'gufi_cmd'
    DEBUG_NAME = 'test'

    RAW_PREFIX = 'raw'

    @staticmethod
    def raw_data_hash(i):
        return '{0}{1}'.format(TestGetConfig.RAW_PREFIX, i)

    def setUp(self):
        self.row_count = 5

        self.db = sqlite3.connect(':memory:')
        hashdb.create_tables(self.db)

        # machine configuration is not used, so
        # don't need to insert extra columns
        machine_hash = 'machine'
        self.db.execute('INSERT INTO {0} (hash) VALUES ("{1}");'.format(
            machine.TABLE_NAME, machine_hash))

        # cmd and debug_name are returned from the
        # gufi configuration, so fill them in
        gufi_hash = 'gufi_cmd'
        self.db.execute('''
                        INSERT INTO {0} (hash, cmd, debug_name)
                        VALUES ("{1}", "{2}", "{3}");
                        '''.format(gufi.TABLE_NAME, gufi_hash,
                                   TestGetConfig.GUFI_CMD,
                                   TestGetConfig.DEBUG_NAME))

        # all rows in the raw_data table point to
        # the same machine and gufi configurations
        for i in range(self.row_count):
            rd_hash = TestGetConfig.raw_data_hash(i)
            self.db.execute('''
                            INSERT INTO {0} (hash, machine_hash, gufi_hash)
                            VALUES ("{1}", "{2}", "{3}");
                            '''.format(raw_data.TABLE_NAME,
                                       rd_hash,
                                       machine_hash,
                                       gufi_hash))

            self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_not_found(self):
        with self.assertRaises(KeyError):
            hashdb.get_config_with_con(self.db, str(self.row_count))

    def test_ok(self):
        for i in range(self.row_count):
            gufi_cmd, debug_name = hashdb.get_config_with_con(self.db, self.raw_data_hash(i))
            self.assertEqual(TestGetConfig.GUFI_CMD, gufi_cmd)
            self.assertEqual(TestGetConfig.DEBUG_NAME, debug_name)

    def test_multiple(self):
        with self.assertRaises(ValueError):
            hashdb.get_config_with_con(self.db, TestGetConfig.RAW_PREFIX)

if __name__ == '__main__':
    unittest.main()