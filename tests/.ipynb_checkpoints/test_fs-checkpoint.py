# Copyright 2020 Iguazio
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

from datetime import datetime, timezone
from os.path import dirname

import pytest

from v3iofs import V3ioFS
from v3iofs.fs import parse_time
from v3iofs.path import split_container

container = 'bigdata'  # TODO: Configuration


def create_file(client, path):
    body = datetime.now().isoformat().encode('utf-8')
    client.put_object(container, path, body=body)


def test_ls(fs: V3ioFS):
    dir = 'v3io-fs-test'
    create_file(fs._client, f'{dir}/test-file')  # Make sure dir exists
    path = f'/{container}/{dir}/'
    out = fs.ls(path)
    assert len(out) > 0, 'nothing found'
    assert all(isinstance(p, dict) for p in out), 'not dict'

    out = fs.ls(path, detail=False)
    assert len(out) > 0, 'nothing found'
    assert all(isinstance(p, str) for p in out), 'not string'


def test_rm(fs: V3ioFS, tmp_obj):
    path = tmp_obj.path
    print(path)
    fs.rm(path)
    print(f"dirname:  {dirname(path)}")
    out = fs.ls(dirname(path), detail=False)
    print(out)
    assert path not in out, 'not deleted'


def test_touch(fs: V3ioFS, tmp_obj):
    path = tmp_obj.path
    fs.touch(path)
    container, path = split_container(path)
    resp = fs._client.get_object(container, path)
    assert resp.body == b'', 'not truncated'


now = datetime(2020, 1, 2, 3, 4, 5, 6789, tzinfo=timezone.utc)
parse_time_cases = [
    # value, expected, raises
    ('', None, True),
    (now.strftime('%Y-%m-%d'), None, True),
    (now.strftime('%Y-%m-%dT%H:%M:%S.%f%z'), now.timestamp(), False),
    (now.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), now.timestamp(), False),
]


@pytest.mark.parametrize('value, expected, raises', parse_time_cases)
def test_parse_time(value, expected, raises):
    if raises:
        with pytest.raises(ValueError):
            parse_time(value)
        return

    out = parse_time(value)
    assert expected == out
