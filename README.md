# Shelf Notes
A small Python store handover board. Submit a note and refresh to see the latest 50 notes. SQLite stores notes in a named volume mounted at /data. Run these commands in the folder containing compose.yaml.

## Run on EC2
1. Check host port 19437 with `sudo ss -ltn 'sport = :19437'` and `sudo docker ps --filter publish=19437`. If occupied, choose an unused host port in compose.yaml and use it in the security group and browser URL.
2. Run `sudo docker compose up -d --build --wait`.
3. Check `sudo docker compose ps` and `curl -i http://127.0.0.1:19437/health`.
4. Allow inbound TCP 19437 from your public IPv4 /32 on the instance security group. Open http://YOUR_EC2_PUBLIC_IP:19437/ from that network. Use a public subnet with an Internet Gateway and an instance public IPv4 address.
5. Add a sample note. Run `sudo docker compose down` then `sudo docker compose up -d --wait`. Refresh to verify persistence.
6. Read logs with `sudo docker compose logs --tail 30 web`. Stop with `sudo docker compose stop`.

The app has no login. Use sample data and restrict the HTTP lab to your IP. Volumes survive ordinary compose down; down -v deletes the notes. The internal HTTP port is 19337. SQLite needs no network port.
