#!/usr/bin/env bash
set -e

nosetests
curl 'https://raw.github.com/WilliamMayor/Dropbox-Uploader/master/dropbox_uploader.sh' -o dropbox_uploader.sh
chmod +x dropbox_uploader.sh
./dropbox_uploader.sh upload . /