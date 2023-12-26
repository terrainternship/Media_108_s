#!/bin/bash

if [[ "${1}" == "worker" ]]; then
    celery -A checker worker -l info
elif [[ "${1}" == "beat" ]]; then
    celery -A checker beat -l info
elif [[ "${1}" == "flower" ]]; then
    celery -A checker flower --port=5555 -l info
fi