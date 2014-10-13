#!/bin/bash
HERE=$(dirname $(readlink -f $0))
cd $HERE/..
if [ ! -d nginx ] ; then
    git clone https://github.com/nginx/nginx
fi

cd nginx

python $HERE/_parser.py src/



