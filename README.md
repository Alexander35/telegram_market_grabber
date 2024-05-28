

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




## example of a user telegram Config
```json
{
  "telegram_grabber_api_id": 1000000,
  "telegram_grabber_api_hash": "xxxxxxxxx",
  "telegram_grabber_app_name": "advgrabber",
  "telegram_grabber_conf": {
         "send_reports_to": "AlexanderIvanov35",
         "chats":
             [
                 {
                     "name": "https://t.me/montenegro_market",
                     "time_shift": "1 day"
                 }
             ],
         "csv_headers": [
             "active_boolean",
             "address_geographic_address",
             "auto_boolean",
             "condition_option_condition",
             "contact_text",
             "description_text",
             "lang_text",
             "link_text",
             "name_text",
             "picture_list_image",
             "price_number",
             "tg_text"]
     }
}
```

```
curl -X 'PATCH' \
  'http://127.0.0.1:10000/telegram_user_configuration' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NjQwZWFjZi03NWI4LTRmMDEtYTQzMy1mNTNlMTA1YTE5YmYiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTcxNjM5NzYzNn0.Jf59uicOihZR7NDlAWXVljXQYdoWXVqUuiNsqyf-Fe4' \
  -H 'Content-Type: application/json' \
  -d '{
  "telegram_grabber_api_id": 10694985,
  "telegram_grabber_api_hash": "a4799614591c8f101beafa1707d48c35",
  "telegram_grabber_app_name": "advgrabber",
  "telegram_grabber_conf": {
         "send_reports_to": "AlexanderIvanov35",
         "chats":
             [
                 {
                     "name": "https://t.me/montenegro_market",
                     "time_shift": "1 hour"
                 }
             ],
         "csv_headers": [
             "active_boolean",
             "address_geographic_address",
             "auto_boolean",
             "condition_option_condition",
             "contact_text",
             "description_text",
             "lang_text",
             "link_text",
             "name_text",
             "picture_list_image",
             "price_number",
             "tg_text"]
     }
}'
```