from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
import requests
import os

API_URL = "http://127.0.0.1:5050"  # ajuste para sua API

class LoginScreen(Screen):
    def fazer_login(self):
        email = self.ids.email.text
        senha = self.ids.senha.text
        try:
            r = requests.post(f"{API_URL}/login", json={"email": email, "senha": senha})
            resposta = r.json()
            self.ids.msg.text = resposta.get("mensagem", "Sem resposta")
        except Exception as e:
            self.ids.msg.text = f"Erro: {str(e)}"

class RegistroScreen(Screen):
    def fazer_registro(self):
        email = self.ids.email.text
        senha = self.ids.senha.text
        confirmar = self.ids.confirmar.text

        if senha != confirmar:
            self.ids.msg.text = "As senhas não conferem!"
            return

        try:
            r = requests.post(f"{API_URL}/register", json={"email": email, "senha": senha})
            resposta = r.json()
            self.ids.msg.text = resposta.get("mensagem", "Sem resposta")
        except Exception as e:
            self.ids.msg.text = f"Erro: {str(e)}"

class Gerenciador(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        kv_path = os.path.join(os.path.dirname(__file__), "telas.kv")
        Builder.load_file(kv_path)
        return Gerenciador()

if __name__ == "__main__":
    MyApp().run()
