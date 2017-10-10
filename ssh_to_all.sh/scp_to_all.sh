#!/bin/bash

set -eu
set -o pipefail
set +o posix

[ $# -lt 2 ] && echo "Usage: $0 <src> <dst>" && exit 1

echo '----------------'
echo "----- Show -----"
echo '----------------'
cat <( cat /data/list | awk '{cmd="scp -o StrictHostKeyChecking=no -r -i x.pem '"$1"' "$2"@"$1":'"$2"'";print cmd}' )
echo ''

echo '----------------'
echo "----- Exec -----"
echo '----------------'
sh -x <( cat /data/list | awk '{cmd="scp -o StrictHostKeyChecking=no -r -i x.pem '"$1"' "$2"@"$1":'"$2"'";print cmd}' )
echo ''
