# Production install (run once)

## Web service (systemd)
sudo cp deploy/dolce-mailer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now dolce-mailer
systemctl status dolce-mailer          # should say active (running)

## HTTPS (Caddy)
sudo apt install -y caddy
echo 'mailer.dolceclinic.com {
    reverse_proxy 127.0.0.1:8080
}' | sudo tee /etc/caddy/Caddyfile
sudo systemctl reload caddy
# Requires the DNS A record: mailer -> 145.223.88.35 (Wix DNS panel)
# Check: https://mailer.dolceclinic.com/approve/test -> "Unknown campaign link" page

## Cron (crontab -e, paste from cron.example with full paths)
*/15 * * * * cd /home/clawdbot/dolce/dolce-polished-core/mailer && .venv/bin/python -m dolce_mailer.welcome_job >> ~/dolce/mailer.log 2>&1
*/5  * * * * cd /home/clawdbot/dolce/dolce-polished-core/mailer && .venv/bin/python -m dolce_mailer.campaigns send-approved >> ~/dolce/mailer.log 2>&1
0 7  * * *   cd /home/clawdbot/dolce/dolce-polished-core/mailer && .venv/bin/python -m dolce_mailer.birthday_job >> ~/dolce/mailer.log 2>&1

NOTE: enable the cron entries only after the Brevo test send succeeds -
until then the welcome job will just log the activation error every 15 min.
