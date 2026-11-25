#! /bin/bash

# To permit this cgi, replace # on the first line above with the
# appropriate #!/path/to/sh shebang, and set this script executable
# with chmod 755.
#

# disable filename globbing
set -f

echo 'Content-type: content-type: application/json'
echo

#exec 2>&1
env 1>&2

_oldIFS="${IFS}"
IFS='&'
set -- ${QUERY_STRING}
query_string_array=( "$@" )
IFS="${_oldIFS}"

for query_arg in "${query_string_array[@]}"
do
    case "${query_arg}" in
	[Vv][Ii][Nn]=*)
	    vin="${query_arg:4}"
	    ;;
	*)
	    echo "Skipped query arg ${query_arg}" 1>&2
	    ::
    esac
done

if [[ -z "${vin}" ]]
then
    # VIN argument is not provided
    exit 1
fi

export RUN_STATES_DIR="${VINDECODER_EU_CACHE_DIR}"
export VINDECODER_EU_CREDENTIAL_FILE="${VINDECODER_EU_CREDENTIAL_FILE}"

decoded_vin_stdout=$( mktemp -u --suffix=_stdout.txt )
decoded_vin_stderr=$( mktemp -u --suffix=_stderr.txt )

${VINDECODER_EU_CLIENT} "${input_for_vin}" 1>${decoded_vin_stdout} 2>${decoded_vin_stderr}
status=$?

if [[ ${status} -eq 0 ]]
then
    _error_=true
else
    _error_=false
fi

if ${_error_}
then
    :
else
    cat ${decoded_vin_stdout}
fi

rm -f ${decoded_vin_stdout} ${decoded_vin_stderr}
	
if ${_error_}
then
    exit 1
else
    exit 0
fi
