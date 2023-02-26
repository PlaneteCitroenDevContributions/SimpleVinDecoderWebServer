#! /bin/bash

# To permit this cgi, replace # on the first line above with the
# appropriate #!/path/to/sh shebang, and set this script executable
# with chmod 755.
#

# disable filename globbing
set -f

echo "Content-type: text/plain; charset=iso-8859-1"
echo

#exec 2>&1

_body_file_=$( mktemp --suffix=_body.txt )
cat > ${_body_file_}

_error_=false
_error_message_=''
if [[ "${REQUEST_METHOD}" != 'POST' ]]
then
    _error_=true
    _error_message_='Only PUT method is supported'
fi

if ! ${_error_}
then
    # keep only alphanum characters from first line
    input_for_vin=$( head -1 ${_body_file_} | tr --complement --delete '[:alnum:]' )

    export RUN_STATES_DIR="${VINDECODER_EU_CACHE_DIR}"
    export VINDECODER_EU_CREDENTIAL_FILE="${VINDECODER_EU_CREDENTIAL_FILE}"

    decoded_vin_stdout=$( mktemp -u --suffix=_stdout.txt )
    decoded_vin_stderr=$( mktemp -u --suffix=_stderr.txt )

    ${VINDECODER_EU_CLIENT} "${input_for_vin}" 1>${decoded_vin_stdout} 2>${decoded_vin_stderr}
    status=$?

    if [[ ${status} -eq 0 ]]
    then
	cat ${decoded_vin_stdout}
	_error_=false
    else
	_error_=true
	_error_message_=$( cat ${decoded_vin_stderr} )
    fi

    rm -f ${decoded_vin_stdout} ${decoded_vin_stderr}
	
fi

rm -f ${_body_file_}

if ${_error_}
then
    echo "service_error_status: 1"
    echo "service_error_message: ${_error_message_}"
else
    echo "service_error_status: 0"
fi
