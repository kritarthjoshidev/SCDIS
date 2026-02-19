# Deploy Guide: Backend on Oracle Always Free VM + Frontend on Vercel

This guide runs the backend on an Oracle Cloud VM and the frontend on Vercel.

## 1) Create Oracle Always Free VM

1. In OCI Console, create a compute instance (Ubuntu or Oracle Linux).
2. Choose an Always Free shape.
3. Enable public IPv4.
4. Keep SSH key ready.

## 2) Open Required Ingress Ports in OCI

Open inbound TCP:

- `22` (SSH)
- `80` (HTTP)
- `443` (HTTPS, optional but recommended)

Use the instance VCN security list/network security group rules.

## 3) SSH into VM and clone project

```bash
ssh -i <your-key.pem> ubuntu@<vm-public-ip>
```

For Oracle Linux images the default user can be `opc` instead of `ubuntu`.

```bash
sudo mkdir -p /opt/scdis
sudo chown -R $USER:$USER /opt/scdis
cd /opt/scdis
git clone https://github.com/<your-username>/<your-repo>.git .
```

## 4) Run backend setup script

From repo root on VM:

```bash
bash backend/deploy/oracle_vm_setup.sh /opt/scdis ubuntu
```

If your VM user is `opc`:

```bash
bash backend/deploy/oracle_vm_setup.sh /opt/scdis opc
```

This script:

- Installs Python + nginx
- Creates backend virtualenv
- Installs backend dependencies
- Sets up systemd service (`scdis-backend`)
- Configures nginx reverse proxy to backend (`127.0.0.1:8010`)

## 5) Verify backend

```bash
curl http://127.0.0.1:8010/
curl http://<vm-public-ip>/
curl http://<vm-public-ip>/openapi.json
```

## 6) Deploy frontend to Vercel

1. Import repository in Vercel.
2. Set Root Directory to `frontend`.
3. Add environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=http://<vm-public-ip>
```

4. Deploy.

## 7) Optional: Add HTTPS on Oracle VM

Point your domain DNS `A` record to VM public IP, then run:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

Then set Vercel env var:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
```

Redeploy frontend after env updates.

## 8) Useful Ops Commands

```bash
sudo systemctl status scdis-backend
sudo journalctl -u scdis-backend -f
sudo systemctl restart scdis-backend

sudo nginx -t
sudo systemctl restart nginx
```

## 9) Common Issues

- 404 from frontend:
  - `NEXT_PUBLIC_API_BASE_URL` points to wrong backend.
  - Check backend routes in `http://<backend>/openapi.json`.
- CORS/network:
  - Verify OCI ingress rules and VM firewall.
- Backend not starting:
  - Check logs: `sudo journalctl -u scdis-backend -f`.
