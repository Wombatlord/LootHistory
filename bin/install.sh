#! /bin/bash

LOOTHISTORY_WORKINGDIR=$1
cd $LOOTHISTORY_WORKINGDIR || echo 'invalid working dir' 1>&2; exit 1

# Check python version, exit status 1 if wrong version. >3.7 required for dataclasses.
if [[ $(python --version | sed 's/\.//g' | cut -c-2) -gt 36 ]]
then
  echo 'update python to 3.7 or higher' 1>&2
  exit 1
fi

# subshell to install venv & requirements.txt, stdout redirected to stderr.
{
  python -m virtualenv venv
  python -m pip install -r "${LOOTHISTORY_WORKINGDIR}/requirements.txt"
} 1>&2

# Voodoo fuckery to find out the directory this script is in.
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Include path export for executable shell scripts in rc file.
DEST=""
if [ -f "$HOME/.bashrc" ]
then
  DEST="$HOME/.bashrc"
else
  [ -f "$HOME/.zshrc" ] && DEST="$HOME/.zshrc"
fi
[ "${DEST}" == "" ] && echo "no rc file found!" 1>&2; exit 1

# Print export to appropriate rc file
echo "export PATH=${SCRIPT_DIR}:${PATH}" >> "${DEST}"

# Print source ~/.bashrc / .bashrc / .zshrc etc. to sdtout.
echo "source ${DEST}"
