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



from performance_pkg import common

# common functions used to process multiple debug prints

def create_table(con, table_name, columns):
    # all column names need to be surrounded by quotation marks, even ones that don't have spaces
    cols = ', '.join('"{0}" {1}'.format(col, common.TYPE_TO_SQLITE[type]) for col, type in columns)
    con.execute('CREATE TABLE {0} ({1});'.format(table_name, cols))

def process_line(line, event, rstrip=None):
    line = line.strip().rstrip(rstrip)
    if line == '':
        return {}
    return {event: line}

# helper function
def format_value(value, type): # pylint: disable=redefined-builtin
    # pylint: disable=no-else-return
    if type is None:
        return 'NULL'
    elif type == str:
        return '"{0}"'.format(value)
    return str(value)

def insert(con, parsed, table_name, columns):
    cols = ', '.join('"{0}"'.format(col) for col, _ in columns)
    vals = ', '.join(format_value(parsed[col], type) for col, type in columns)
    con.execute('INSERT INTO {0} ({1}) VALUES ({2});'.format(table_name, cols, vals))

def cumulative_times_extract(src, commit, branch, columns):
    # these aren't obtained from running gufi_query
    data = {
        'id'    : None,
        'commit': commit,
        'branch': branch,
    }

    # Organize Column Names longest->shortest
    #
    # Column names that are substrings of other column names will be
    # processed last to avoid parsing the longer column name incorrectly
    sorted_columns = [value[0] for value in columns]
    sorted_columns.sort(key=len)
    sorted_columns.reverse()

    # parse input
    for line in src:
        line = line.strip()
        if line == '':
            continue

        for value in sorted_columns:
            if value == line[:len(value)]:
                line = line[len(value):]
                if line == '':
                    continue
                if line[0] == ":":
                    line = line[1:]
                data.update(process_line(line, value, 's'))
                break

    # check for missing input
    for col, _ in columns:
        if col not in data:
            raise ValueError('Cumulative times data missing "{0}" on commit {1}'.format(col, commit))

    return data
