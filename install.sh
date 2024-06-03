#!/bin/bash


ACTION=$1
APP_NAME=easynordvpn
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

PATH_SAVE=/opt/${APP_NAME}
PATH_EXEC=/usr/local
EXEC_CMD=$APP_NAME
EXEC_RUN=${PATH_EXEC}/bin
EXEC_ICON=${PATH_EXEC}/share/icons
EXEC_MENU=${PATH_EXEC}/share/applications

echo ""
if [ "$ACTION" = "global" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo "This installation requires root privilege to execute"
        echo ""
        exit
    fi
elif [ "$ACTION" = "local" ]; then
    PATH_EXEC=$HOME/.local/share
    PATH_SAVE=$PATH_EXEC/${APP_NAME}
    EXEC_CMD=$PATH_SAVE/${APP_NAME}
    EXEC_RUN=$PATH_SAVE
    EXEC_ICON=$PATH_EXEC/icons
    EXEC_MENU=$PATH_EXEC/applications
elif [ "$ACTION" = "remove" ]; then
    rm -f $HOME/.local/share/applications/${APP_NAME}.desktop
    rm -f $HOME/.local/share/icons/${APP_NAME}.png
    rm -rf $HOME/.local/share/${APP_NAME}
    echo "Local files removed"

    if [ "$EUID" -eq 0 ]; then
        rm -f /usr/local/share/applications/${APP_NAME}.desktop
        rm -f /usr/local/share/icons/${APP_NAME}.png
        rm -f /usr/local/bin/${APP_NAME}
        rm -rf /opt/${APP_NAME}
        echo "Global files also removed"
    else
        echo "If globally installed, run as root user."
    fi
    echo ""
    exit
else
    echo "$> bash install.sh [OPTION] "
    echo "     or, after 'chmod +x install.sh':"
    echo "$> ./install.sh [OPTION] "
    echo ""
    echo "Available options:"
    echo "   global - As root, install for all users at /opt/ and /usr/local/"
    echo "   local  - Locally, on your HOME/.local/share/"
    echo "   remove - Uninstall, run as root if installed global"
    echo "   help   - Prints this help message"
    echo ""
    exit
fi

EXEC_NAME=${APP_NAME}.py
ICON_NAME=${APP_NAME}.png
MENU_NAME=${APP_NAME}.desktop
INST_NAME=install.sh
READ_NAME=README.md

mkdir -p $PATH_SAVE
mkdir -p $EXEC_RUN
mkdir -p $EXEC_ICON
mkdir -p $EXEC_MENU
cp -R --remove-destination ${SCRIPT_DIR}/${EXEC_NAME} ${PATH_SAVE}/ > /dev/null 2>&1
cp -R --remove-destination ${SCRIPT_DIR}/${ICON_NAME} ${PATH_SAVE}/ > /dev/null 2>&1
cp -R --remove-destination ${SCRIPT_DIR}/${MENU_NAME} ${PATH_SAVE}/ > /dev/null 2>&1
cp -R --remove-destination ${SCRIPT_DIR}/${INST_NAME} ${PATH_SAVE}/ > /dev/null 2>&1
cp -R --remove-destination ${SCRIPT_DIR}/${READ_NAME} ${PATH_SAVE}/ > /dev/null 2>&1

chmod +x ${PATH_SAVE}/${EXEC_NAME}
chmod +x ${PATH_SAVE}/${INST_NAME}
ln -s ${PATH_SAVE}/${EXEC_NAME} ${EXEC_RUN}/${APP_NAME}

cp ${PATH_SAVE}/${ICON_NAME} ${EXEC_ICON}/${ICON_NAME}

fc=$( < ${PATH_SAVE}/${MENU_NAME} )
echo "${fc//|EXEC_CMD|/${EXEC_CMD}}" > ${EXEC_MENU}/${MENU_NAME}

echo "Successfully installed."
echo ""
