

# Start & rebuild the project by docker
```bash
docker compose up --build
```

###  Remove the old images & containers
```bash
docker rm -vf $(docker ps -aq)
docker rmi -f $(docker images -aq)
```

# Add a new migration 
```bash
alembic revision --autogenerate -m "xxxxx"
```

# Push a commit with the different ssh key
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519xxx
```

# Make a dev request to API
```bash
curl -k -X 'PATCH' \
  'https://127.0.0.1/users/me' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer xxx.yyy.zzz' \
  -d '{
    "ux_conf": {
      "conf": {
        "adc": "cdf"
      }
    }
  }'
-k to ignore cert
```
