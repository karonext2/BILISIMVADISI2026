from __future__ import annotations

import config
from clients.evren_client import get_evren_client

def main():
    client = get_evren_client()

    models = client.models.list()
    print("EVREN bağlantısı başarılı.")
    print("\nModeller:")
    for model in models.data:
        print("-", model.id)

    r = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Sadece TAMAM yaz."
            }
        ],
        max_tokens=20,
        temperature=0.0,
    )
    print("\nllm-fast testi:", r.choices[0].message.content)

if __name__ == "__main__":
    main()
