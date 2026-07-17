# Production operations

The production host runs the Compose project from `/home/ashish/pingbot_v2`.

## Managed host configuration

- Install `ssh/99-pingbot-hardening.conf` as
  `/etc/ssh/sshd_config.d/99-pingbot-hardening.conf`, validate with `sshd -t`,
  and reload SSH only after a second key-authenticated session succeeds.
- Install `fail2ban/sshd.local` as `/etc/fail2ban/jail.d/sshd.local`.
- Install the certificate renewal service and timer from `systemd/` in
  `/etc/systemd/system/`, then enable `pingbot-cert-renew.timer`.
- Install `tmpfiles/pingbot-log-archive.conf` in `/etc/tmpfiles.d/` so archived
  pre-hardening nginx logs are removed after 14 days.

The host firewall permits TCP 80 and 443 and rate-limits TCP 22. Redis and
Gunicorn are intentionally available only on the private Compose network.

## Certificate renewal

Run a staging renewal test without stopping nginx:

```sh
sudo ./renew_certs.sh --dry-run
```

Inspect the timer and its latest result:

```sh
systemctl list-timers pingbot-cert-renew.timer
journalctl -u pingbot-cert-renew.service
```

## Deployment checks

After a deployment or reboot, confirm that all services are running and that
the public readiness endpoint succeeds:

```sh
sudo docker compose ps
curl --fail --silent --show-error https://emapingbot.com/health/ready
```
