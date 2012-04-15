#!/bin/bash
IFS=$'\n'

function traversedir {
    local DIR=$1
    for file in `ls "$DIR"`; do
        if [ -d "$DIR/$file" ]; then
            traversedir $DIR/$file
        else
            createfile $file $DIR
        fi
    done
}

function createfile {
    SUBDIR=`echo "$2" | sed "s/$TOPDIR\/\(.*\)/\1/"`
    mkdir -p $TARGET/$SUBDIR
    touch $TARGET/$SUBDIR/$1
}


if [ "$1" = "-h" -o "$1" = "--help" ]; then
    echo "usage " $0 " from to"
    exit 1
fi

TOPDIR=`dirname "$1" | sed 's/\//\\\\\//g'`

TARGET=$2

traversedir "$1"