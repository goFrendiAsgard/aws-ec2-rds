#!/bin/bash
mkdir -p ./pulumiLock
export PULUMI_BACKEND_URL="file://./pulumiLock"
export PULUMI_CONFIG_PASSPHRASE=
pulumi stack output
