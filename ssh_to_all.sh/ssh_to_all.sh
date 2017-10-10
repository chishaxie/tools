#!/bin/bash

set -eu
set -o pipefail
set +o posix

[ $# -eq 0 ] && echo "Usage: $0 <cmd>" && exit 1

echo '----------------'
echo "----- Show -----"
echo '----------------'
cat <( cat /data/list | awk '{cmd="ssh -o StrictHostKeyChecking=no -t -i x.pem -l"$2" "$1" '"$1"'";print cmd}' )
echo ''

echo '----------------'
echo "----- Exec -----"
echo '----------------'
sh -x <( cat /data/list | awk '{cmd="ssh -o StrictHostKeyChecking=no -t -i x.pem -l"$2" "$1" '"$1"'";print cmd}' )
echo ''
