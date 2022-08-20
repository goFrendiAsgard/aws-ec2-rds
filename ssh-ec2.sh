#!/bin/bash
mkdir -p ./pulumiLock
export PULUMI_BACKEND_URL="file://./pulumiLock"
export PULUMI_CONFIG_PASSPHRASE=
ssh -i app-keypair ubuntu@$(pulumi stack output app-eip-public-dns)