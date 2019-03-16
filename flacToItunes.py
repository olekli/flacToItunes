#!/usr/local/bin/python3

# Copyright 2019 Ole Kliemann
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import mutagen
import sys
import tempfile
import subprocess
import os

metadataMapping = {
    'artist': 'artist',
    'album': 'album',
    'title': 'name',
    'albumartist': 'album artist',
    'tracknumber': 'track number',
    'date': 'year',
    'comment': 'comment'
  }

def mkScriptHead(filename):
  return [
      'set thisFile to POSIX file \"' + filename + '\" as alias',
      'tell application \"iTunes\"',
      'set thisTrack to add thisFile',
    ]

def mkScriptTail():
  return ['end tell']

def mkMetadataAssignment(field, value):
  return 'set ' + field + ' of thisTrack to \"' + value + '\"'

def mkScriptMetadata(metadata):
  result = []
  for key in metadata:
    if key in metadataMapping:
      result.append(mkMetadataAssignment(metadataMapping[key], metadata[key][0]))
  return result

def mkScriptConvert():
  return [
      'set old_encoder to current encoder',
      'set current encoder to encoder "Lossless Encoder"',
      'convert thisTrack',
      'set current encoder to old_encoder',
      'delete thisTrack'
    ]

def mkScript(filename, metadata):
  return mkScriptHead(filename) + \
         mkScriptMetadata(metadata) + \
         mkScriptConvert() + \
         mkScriptTail()

def mkOsascriptCommandline(script):
  return [ 'osascript' ] + [ x for y in script for x in [ '-e', y ] ]

def getMetadata(filename):
  return mutagen.File(filename)

def addFile(filename):
  with tempfile.TemporaryDirectory() as tmpdir:
    filename_wave = os.path.join(tmpdir, os.path.splitext(filename)[0] + '.wav')
    subprocess.run(
        ['flac', '-d', '-o', filename_wave, filename],
        check=True
      )
    metadata = getMetadata(filename)
    script = mkScript(filename_wave, metadata)
    script_commandline = mkOsascriptCommandline(script)
    subprocess.run(script_commandline, check=True)
    print('added file: ' + filename)
    print(str(metadata))

for filename in sys.argv[1:]:
  addFile(filename)
