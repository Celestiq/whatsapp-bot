import os
from fastapi import FastAPI, Request, HTTPException
import requests
import logging
from fastapi import Query

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Use env vars for security
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    logging.info(f"Params: mode={hub_mode}, token={hub_verify_token}, challenge={hub_challenge}")
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logging.info("Verification successful!")
        return hub_challenge  # Plain text response
    else:
        logging.info("Verification failed!")
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    for message in value["messages"]:
                        if message.get("type") == "text":
                            from_number = message["from"]
                            user_text = message["text"]["body"]

                            # Your append logic (or echo: reply_text = user_text)
                            reply_text = user_text + " - appended_number_123"

                            # Send reply
                            send_message(from_number, reply_text)

    return {"status": "ok"}

def send_message(to_number: str, text: str):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }
    response = requests.post(url, json=payload, headers=headers)
    logging.info(f"Reply sent: {response.json()}")  # Logs for debugging

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)