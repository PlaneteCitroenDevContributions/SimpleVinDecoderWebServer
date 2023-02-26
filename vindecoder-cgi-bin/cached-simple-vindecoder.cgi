#! /bin/bash

# To permit this cgi, replace # on the first line above with the
# appropriate #!/path/to/sh shebang, and set this script executable
# with chmod 755.
#

# disable filename globbing
set -f

echo "Content-type: text/plain; charset=iso-8859-1"
echo

exec 2>&1

echo CGI/1.0 test script report:
echo

echo argc is $#. argv is "$*".
echo

echo SERVER_SOFTWARE = $SERVER_SOFTWARE
echo SERVER_NAME = $SERVER_NAME
echo GATEWAY_INTERFACE = $GATEWAY_INTERFACE
echo SERVER_PROTOCOL = $SERVER_PROTOCOL
echo SERVER_PORT = $SERVER_PORT
echo REQUEST_METHOD = $REQUEST_METHOD
echo HTTP_ACCEPT = "$HTTP_ACCEPT"
echo PATH_INFO = "$PATH_INFO"
echo PATH_TRANSLATED = "$PATH_TRANSLATED"
echo SCRIPT_NAME = "$SCRIPT_NAME"
echo QUERY_STRING = "$QUERY_STRING"
echo REMOTE_HOST = $REMOTE_HOST
echo REMOTE_ADDR = $REMOTE_ADDR
echo REMOTE_USER = $REMOTE_USER
echo AUTH_TYPE = $AUTH_TYPE
echo CONTENT_TYPE = $CONTENT_TYPE
echo CONTENT_LENGTH = $CONTENT_LENGTH

echo '===================DEBUG======================='

echo '===================EXPORTS======================='
date
export
echo '===================END EXPORTS======================='

set -x

cat > /tmp/body.txt

echo 'BODY:'
cat /tmp/body.txt
echo 'BODY END'

_error_=false
_error_message_=''
if [[ "${REQUEST_METHOD}" != 'POST' ]]
then
    _error_=true
    _error_message_='Only PUT method is supported'
fi


echo '===================CALL VIN DECODER======================='
if ! ${_error_}
then
    export RUN_STATES_DIR="${VINDECODER_EU_CACHE_DIR}"
    export VINDECODER_EU_CREDENTIAL_FILE="${VINDECODER_EU_CREDENTIAL_FILE}"

    decoded_vin=$( ${VINDECODER_EU_CLIENT} "${vin}" )
    status=$?
fi
echo '===================CALL DONE======================='


echo '===================FINAL OUT======================='
if ${_error_}
then
    echo "service_error_status: 1"
    echo "service_error_message: ${_error_message_}"
else
    echo "service_error_status: 0"
fi
