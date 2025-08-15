# macro-brief-LINE-bot

Kubernetes-ready Docker app that summarizes recent macro news especially for **gold (XAU)** watchers using the OpenAI API, then **pushes the brief to LINE**.

## Features

- **One-shot daily brief**: Generates a concise summary tailored to XAU.
- **Opinionated structure**: Headline + sections like *Macro & Monetary Policy*, *USD & Yields*, *Flows (ETF/Central Bank/Speculative)*, *Geopolitics & Other*.
- **LINE push**: Sends the result to a specified LINE user, group, or room via the Messaging API.
- **Container-first**: Small Python 3.11 image; easy to run as a Kubernetes CronJob.

## How it works

1. `app/gpt_client.py` builds a prompt geared to XAU and calls the **OpenAI Responses API** (model configurable).
2. `app/line_client.py` pushes the generated text to LINE’s **/v2/bot/message/push** endpoint.
3. `app/main.py` wires the two together for a single execution (perfect for cron/CronJob).

## Requirements

- Python **3.11+** (for local runs) or Docker
- An **OpenAI API key**
- A **LINE Messaging API** channel with a **Channel access token**
- The **recipient ID** (user, group, or room) that the bot is allowed to push to

> Note: The recipient must have added/friended the bot, or be in a group/room with the bot, for push to succeed.

## Environment variables

| Name                       | Required | Example / Default        | Description |
|---------------------------|----------|---------------------------|-------------|
| `OPENAI_API_KEY`          | ✅        | `sk-...`                  | OpenAI API key (used by the SDK). |
| `OPENAI_MODEL`            | ⛳        | `gpt-5-mini`              | OpenAI model name for the Responses API. |
| `LINE_CHANNEL_ACCESS_TOKEN` | ✅      | `eyJ...`                  | LINE Messaging API channel access token. |
| `LINE_TO`                 | ✅        | `Uxxxxxxxxxxxxxxxxxxxx`   | Target userId / groupId / roomId to push the message to. |
| `TZ`                      | ⛳        | `Asia/Tokyo` (Dockerfile) | Container time zone; prompts use JST. |

## Quick start (local)

```bash
# 1) Clone and enter
git clone <this-repo-url>
cd macro-brief-line-bot-main

# 2) Set env vars (or use a .env tool)
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-5-mini
export LINE_CHANNEL_ACCESS_TOKEN=eyJ...
export LINE_TO=Uxxxxxxxxxxxxxxxxxxxx

# 3) Install deps
pip install -r requirements.txt

# 4) Run once (generates + pushes a brief)
python -m app.main
```

## Run with Docker

```bash
# Build
docker build -t macro-brief-line-bot:local .

# Run (one shot)
docker run --rm \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e OPENAI_MODEL="${OPENAI_MODEL:-gpt-5-mini}" \
  -e LINE_CHANNEL_ACCESS_TOKEN="$LINE_CHANNEL_ACCESS_TOKEN" \
  -e LINE_TO="$LINE_TO" \
  -e TZ=Asia/Tokyo \
  macro-brief-line-bot:local
```

## Kubernetes (CronJob example)

Run this container on a schedule (e.g., 08:30 JST on weekdays). Adjust image, schedule, and secret refs to your cluster.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: macro-brief-line-bot
spec:
  schedule: "30 23 * * 0-4" # 08:30 JST ~= 23:30 UTC (adjust for your cluster TZ)
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: bot
              image: ghcr.io/<YOUR_GH_USERNAME>/macro-brief-line-bot:latest
              env:
                - name: OPENAI_API_KEY
                  valueFrom: { secretKeyRef: { name: openai, key: api_key } }
                - name: OPENAI_MODEL
                  value: "gpt-5-mini"
                - name: LINE_CHANNEL_ACCESS_TOKEN
                  valueFrom: { secretKeyRef: { name: line, key: channel_access_token } }
                - name: LINE_TO
                  valueFrom: { secretKeyRef: { name: line, key: to } }
                - name: TZ
                  value: "Asia/Tokyo"
```

> If your cluster supports `spec.timeZone` on CronJobs, you can set it to `Asia/Tokyo` and keep the schedule in local time.


## Customization

- **Change the market or tone**: Edit the prompt in `app/gpt_client.py` (`build_prompt()`). It’s written to produce a Japanese brief focused on XAU; you can target other assets or languages.
- **Switch models**: Set `OPENAI_MODEL` to your preferred model.
- **Chunking/length**: The code sends one LINE text message per run. If your brief gets long, consider splitting by character count and sending multiple messages.

## Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── gpt_client.py      # Builds prompt + calls OpenAI Responses API
│   ├── line_client.py     # Pushes message to LINE
│   └── main.py            # Entry point (one execution)
├── requirements.txt
├── Dockerfile
├── .github/workflows/build-docker-image.yaml
├── .dockerignore
├── .gitignore
└── LICENSE
```

## Troubleshooting

- **401/403 from LINE**
  Double-check `LINE_CHANNEL_ACCESS_TOKEN` and that the target in `LINE_TO` is valid and reachable by the bot.

- **No message received**
  Ensure the recipient has added/friended the bot or is in the same group/room; verify the ID type (userId vs groupId vs roomId).

- **OpenAI errors**
  Verify `OPENAI_API_KEY`, model availability in your account, and network egress/proxy rules if running in a locked-down environment.

- **Text too long**
  Consider truncating or sending multiple messages if you routinely exceed LINE’s message size.

## License

[MIT](./LICENSE)
