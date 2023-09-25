#!/bin/bash

# Display the pwd
var=$(pwd)
echo "The current working directory $var."

#load env variables
set -a; source dev.env; set +a

# Login Credentials for MYSQL loaded from env file
if [[ "$MYSQL_USER" != "" ]]; then
    echo "loaded credentials for the user named \"$MYSQL_USER\""
fi

