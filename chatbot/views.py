from django.shortcuts import render
from django.http import JsonResponse
import requests
from .models import Chat
from django.utils import timezone
import os
from .agent import ShopyAgent

API_ENDPOINT = "http://127.0.0.1:8001/chat/v1"

def model_qa_api(message):
    api_url = API_ENDPOINT
    payload = {
        "user_input": message
    }

    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        answer = response_data.get("responses")
        print(type(answer))
        return answer
    else:
        return None
    
def model_qa_emb(message):
    agent = ShopyAgent()
    response = agent.run(message=message)
    print(f"en funcion model_qa_emb{response}")
    return response

def chatbot(request):
    chats = Chat.objects.all()

    if request.method == 'POST':
        message = request.POST.get('message')
        
        response = model_qa_emb(message)

        # Guardar mensaje y respuesta en la base de datos
        chat = Chat(message=message, response=response, created_at=timezone.now())
        chat.save()

        response_data = JsonResponse({'message': message, 'response': response})
        return response_data
    
    return render(request, 'chatbot.html', {'chats': chats})
