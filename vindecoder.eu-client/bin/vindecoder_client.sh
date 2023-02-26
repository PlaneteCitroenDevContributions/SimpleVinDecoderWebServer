#! /bin/bash

COMMAND="$0"

: ${RUN_STATES_DIR:=/tmp}

if ! [[ -d "${RUN_STATES_DIR}" && -w "${RUN_STATES_DIR}" ]]
then
    echo "${COMMAND}: ERROR. Path ${RUN_STATES_DIR} not a valid folder" 1>&2
    exit 1
fi

if [[ -r "${VINDECODER_EU_CREDENTIAL_FILE}" ]]
then

    credential_file_effective_content=$(
	sed -e '/^[ \t]*#/d' "${VINDECODER_EU_CREDENTIAL_FILE}"
				     )

    VINDECODER_EU_APIKEY=$(
	grep 'vindecoder.eu_apikey' <<< "${credential_file_effective_content}" | cut -d '=' -f 2 | tr -d ' '
			)

    VINDECODER_EU_SECRETKEY=$(
	grep 'vindecoder.eu_secretkey' <<< "${credential_file_effective_content}" | cut -d '=' -f 2 | tr -d ' '
			   )
   
fi
   
if [[ -z "${VINDECODER_EU_APIKEY}" && -z "${VINDECODER_EU_SECRETKEY}" ]]
then      
    echo "${COMMAND}: ERROR. Vindecoder.eu apikey or secretkey not provided" 1>&2
    exit 1
fi
    
get_vin_data_from_vin_decoder_eu ()
{
    vin="$1"

    cache_file_name="${RUN_STATES_DIR}/cache_data_vin_${vin}.json"

    _tmp_dir_=$( mktemp --directory )

    _vin_json_file_="${_tmp_dir_}/vin.json"

    if [[ -r "${cache_file_name}" ]]
    then
        cp "${cache_file_name}" "${_vin_json_file_}"
    else

        # try to get VIN

        apiPrefix="https://api.vindecoder.eu/3.2"
        apikey="${VINDECODER_EU_APIKEY}"
        secretkey="${VINDECODER_EU_SECRETKEY}"
        id="decode"

        key="${vin}|${id}|${apikey}|${secretkey}"
        sha1_key=$( echo -n "${key}" | sha1sum )

        controlsum=$( echo "${sha1_key}" | cut -c1-10 )

        url="${apiPrefix}/${apikey}/${controlsum}/${id}/${vin}.json"

        curl_out="${_tmp_dir_}/curl_out.txt"
        curl_http_code=$( curl --insecure -s -o "${curl_out}" -w '%{http_code}' "${url}" )
        if [ "${curl_http_code}" -eq 200 ]
        then
            # "Got 200! All done!"
            # keep result in cache
            if grep -q '"error":true' "${curl_out}"
            then
                # resulting json mentions an error
                # TODO: manage these errors
                echo "ERROR while fetching url ${url} to decode VIN ${vin}: result $( cat /tmp/vin.json )" 1>&2
            else
		cp "${curl_out}" "${_vin_json_file_}"
                cp "${_vin_json_file_}" "${cache_file_name}"
            fi
        else
            echo "ERROR while fetching url ${url} to decode VIN ${vin}: code ${curl_http_code}" 1>&2
        fi
    fi

    exit_code=-1
    if [[ -f "${_vin_json_file_}" ]]
    then
	cat "${_vin_json_file_}" | jq -c '."decode"|.[]'
	exit_code=0
    else
	exit_code=1
    fi

    rm -rf "${_tmp_dir_}"
    return ${exit_code}
}

vin="$1"

if [[ -z "${vin}" ]]
then
    echo "${COMMAND} ERROR: no VIN argument provided" 1>&2
    exit 1
fi

get_vin_data_from_vin_decoder_eu "${vin}"
