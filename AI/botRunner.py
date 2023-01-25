import httpx
import random
import json
import torch

from AI.model import NeuralNet
from AI.utils import tokenize, bag_of_words

async def rexlyBot(message):
    with open('AI/intents.json', 'r') as json_data:
        intents = json.load(json_data)
        
    FILE = "AI/RexlyAI.pth"
    data = torch.load(FILE, map_location=torch.device('cpu'))

    #we need these variables from the Rexly file to give the neural network
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data['all_words']
    tags = data['tags']
    model_state = data["model_state"]


    model = NeuralNet(input_size, hidden_size, output_size)
    model.load_state_dict(model_state)
    
    #this is so the model doesn't think it's training
    model.eval()
    #we must tokenize the message before sending it in the model
    message = tokenize(message)
    X = bag_of_words(message, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X)

    output = model(X)
    _, predicted = torch.max(output, dim=1) #gets prediction from model

    tag = tags[predicted.item()]

    #this is the confidence level of how correct the model thinks it is
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    
    if prob.item() > 0.90:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                if intent["action"] == "search_query":
                    #we sent a request to search API and get aresponse of products that were searched
                    async with httpx.AsyncClient() as client:
                        response = await client.post("http://localhost:5000/api/v1/search", data={"query": message})
                        if response.status_code == 500:
                            return "500 Error"
                        elif response.status_code == 400:
                            return "400 Error"
                        response = response.json() #turns response into json format
                    
                    return {
                        "intentResult": random.choice(intent['responses']),
                        "search": response,
                        "tag": tag,
                        "probRes": f"{prob.item():.4f}"
                    }
                #elif intent["action"] == "nextbestproduct":
                #    async with httpx.AsyncClient() as client:
                #        #obviously change to nbp endpoint when possible
                #        response = await client.post("http://localhost:5000/api/v1/nbp")
                #        if response.status_code == 500:
                #            return "500 Error"
                #        elif response.status_code == 400:
                #            return "400 Error"
                #        
                #        response = response.json()
                #    
                #    return {
                #        "intentResult": random.choice(intent['responses']),
                #        "nbp": response,
                #        "tag": tag,
                #        "probRes": f"{prob.item():.4f}"
                #    }
                else:
                    return {
                        'intentResult': random.choice(intent['responses']),
                        "tag": tag,
                        "probRes": f"{prob.item():.4f}"
                    }
    else:
        return {
            'intentResult': "I'm sorry, I don't understand. Please try rephrasing your message in a differnet way",
            "tag": 'no_tag',
            "probRes": f"{prob.item():.4f}"
        }