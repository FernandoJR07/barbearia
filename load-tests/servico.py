import os
import random
import time
from locust import HttpUser, task, between
from dotenv import load_dotenv
from faker import Faker
from pathlib import Path

load_dotenv()

fake = Faker()

class ServicoUser(HttpUser):
    wait_time = between(1, 2)
    token_global = None

    def on_start(self):
        if not ServicoUser.token_global:
            ServicoUser.token_global = self.obter_token()

        self.headers = {
            "Authorization": f"Bearer {ServicoUser.token_global}",
            "Content-Type": "application/json"
        }

    def obter_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "audience": os.getenv("AUTH0_AUDIENCE")
        }

        response = response = self.client.post(
            os.getenv("TOKEN_URL"),
            json=payload,
            name="POST /oauth/token"
        )

        if response.status_code != 200:
            raise Exception(f"Erro Auth0: {response.status_code} | {response.text}")

        token = response.json().get("access_token")
        if not token:
            raise Exception("Access Token não encontrado na resposta do Auth0")
        return token

    @task
    def criar_e_buscar_servico(self):
        payload = {
            "nome": f"Corte {fake.first_name()} {fake.last_name()}",
            "descricao": fake.sentence(nb_words=4),
            "preco": round(random.uniform(30.0, 150.0), 2),
            "ativo": True
        }

        with self.client.post("/servicos", json=payload, headers=self.headers, catch_response=True, name="POST /servicos") as response:
            if response.status_code not in [200, 201]:
                response.failure(f"POST falhou: {response.status_code} | {response.text}")
                return

            try:
                body = response.json()
                servico_id = None
                if isinstance(body, dict):
                    if "dados" in body and isinstance(body["dados"], dict):
                        servico_id = body["dados"].get("id")
                    else:
                        servico_id = body.get("id")

                if not servico_id:
                    response.failure("ID não encontrado no corpo da resposta")
                    return

                self.client.get(f"/servicos/{servico_id}", headers=self.headers, name="GET /servicos/{id}")

            except Exception as e:
                response.failure(f"Erro ao processar JSON: {e}")