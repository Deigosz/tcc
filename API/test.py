import requests

url = "http://localhost:5000/criar_trilha"  # Ajuste se a porta ou domínio forem diferentes

payload = {
    "id_usuario": 1,
    "nome_trilha": "Trilha de Revisão FATEC - Humanas",
    "materias": ["Lógica", "Cultura e Artes"],
    "dificuldades": ["Fácil", "Médio"]
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.text)