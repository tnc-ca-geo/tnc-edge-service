#!/bin/bash


scriptdir="$(dirname -- "$( readlink -f -- "$0")")"

if [ "$UID" -lt 1000 ] ; then
  echo "This script should be run as a non-root user with 'sudo' access"
  exit 1
fi

if ! [ -e "$scriptdir/secret_adduser_ondeck.txt" ] ; then
  echo "Cannot adduser without secrets file containing password"
  exit 1
fi

USERHOME="/home/ondeck"

sudo /bin/bash <<EOF

adduser ondeck < "$scriptdir/secret_adduser_ondeck.txt"

if ! [ -d "$USERHOME/.ssh" ] ; then
  mkdir "$USERHOME/.ssh"
  chmod go-rwx "$USERHOME/.ssh"
  chown ondeck:ondeck "$USERHOME/.ssh"
fi

if ! [ -e "$USERHOME/.ssh/authorized_keys" ] ; then
  touch "$USERHOME/.ssh/authorized_keys"
  chmod go-rwx "$USERHOME/.ssh/authorized_keys"
  chown ondeck:ondeck "$USERHOME/.ssh/authorized_keys"
fi

while read k; do
  if ! grep -q "$k" "$USERHOME/.ssh/authorized_keys" ; then
    echo "$k" >> "$USERHOME/.ssh/authorized_keys"
  fi
done <"$scriptdir/ondeck_authorized_keys.txt"

EOF
