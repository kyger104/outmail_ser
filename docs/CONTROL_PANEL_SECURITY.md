# Control Panel Security

This project now protects control panel data in two layers:

1. Application Basic Auth for every `/api/admin/*` backend endpoint.
2. Optional Cloudflare Access in front of the public hostname.

Changing the visible route alone is not security. Anyone can inspect frontend assets or guess common paths, so the backend API must reject unauthenticated requests.

## Current App Protection

The Vue control panel redirects unauthenticated users to `/login`. Login credentials are stored in `sessionStorage`, so closing the browser tab/session clears them. Axios attaches the `Authorization: Basic ...` header only for `/api/admin/*` requests.

The backend validates the same credentials through `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `backend/.env`. Set a strong password on the server:

```bash
sudo sed -i 's/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=REPLACE_WITH_A_LONG_RANDOM_PASSWORD/' /opt/imap/backend/.env
sudo systemctl restart imap-backend
```

To verify the protection:

```bash
curl -i https://chace123.sbs/api/admin/stats
curl -i -u 'admin:YOUR_PASSWORD' https://chace123.sbs/api/admin/stats
```

The first command should return `401`; the second should return JSON.

## Cloudflare Access Recommendation

Cloudflare can be used here. The recommended setup is Cloudflare Zero Trust Access with a self-hosted application for `chace123.sbs` or a separate admin hostname such as `admin.chace123.sbs`.

Suggested policy:

- Application type: Self-hosted.
- Domain: `chace123.sbs` or `admin.chace123.sbs`.
- Include rule: your exact email address, or a tightly controlled email list.
- Login method: One-time PIN or your preferred identity provider.
- Session duration: short enough for operations, for example 8-24 hours.

Do not configure One-time PIN as a broad include rule for all email addresses. Cloudflare warns that OTP should be paired with a specific email domain or email list; otherwise anyone with an email address can receive a code and reach the protected application.

Keep the app-level Basic Auth even when Cloudflare Access is enabled. Cloudflare protects the edge, while app auth protects the API if DNS, proxy, or future deployment settings change.
