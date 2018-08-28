#!/usr/bin/env bash
if [ -z "${BROWSERSTACK_ACCESS_KEY}" ]; then
  echo "BROWSERSTACK_ACCESS_KEY not set, exiting."
  env
else
  /usr/local/bin/BrowserStackLocal --key "${BROWSERSTACK_ACCESS_KEY}" --force-local
fi
