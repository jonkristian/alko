#!/bin/bash

adb backup -noapk de.alko.intouch
( printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" ; tail -c +25 backup.ab ) |  tar xz
cat apps/de.alko.intouch/sp/de.alko.intouch_preferences.xml | \
    sed 's/&nbsp;/ /g; s/&amp;/\&/g; s/&lt;/\</g; s/&gt;/\>/g; s/&quot;/\"/g; s/#&#39;/\'"'"'/g; s/&ldquo;/\"/g; s/&rdquo;/\"/g;' | \
    grep -o '"[^"]*"\s*:\s*"[^"]*"' | grep -E '^"(client_secret|access_token|refresh_token)"'
