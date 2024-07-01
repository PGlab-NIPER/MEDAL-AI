import random
import json

import torch
from schemas.llama_cpp import LlamaCppModel
from schemas.rag import KGRag

from pathlib import Path

import logging

logger = logging.getLogger('MEDAL-AI')

# from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# with open('intents.json', 'r') as json_data:
#     intents = json.load(json_data)

# FILE = "data.pth"
# data = torch.load(FILE)

# input_size = data["input_size"]
# hidden_size = data["hidden_size"]
# output_size = data["output_size"]
# all_words = data['all_words']
# tags = data['tags']
# model_state = data["model_state"]

# model = NeuralNet(input_size, hidden_size, output_size).to(device)
# model.load_state_dict(model_state)
# model.eval()

model = None
tokenizer = None
rag_pipeline = None

def load_model(model_name):
    global model, tokenizer, rag_pipeline

    if not model:
        model_name = model_name
        path = Path(model_name)
        # path = Path('D:\\workspace\\models\\meditron-7b-q8_0.gguf')
        if path.is_file():
            model_file = path
        else:
            model_file = list(path.glob('*.gguf'))[0]

        logger.info(f"llama.cpp weights detected: \"{model_file}\"")

        # model_file = "D:\\workspace\\KGWork\\llama3_lora_model\\"

        model, tokenizer = LlamaCppModel.from_pretrained(model_file)
        rag_pipeline = KGRag("neo4j", model)
        rag_pipeline.initialise_vector_indexes()

    # rag_pipeline.evaluate_using_rag(file_path="H:\\Downloads\\ori_pqal.json")

    return model, tokenizer

def unload_model():
    global model, tokenizer
    del model
    del tokenizer
    model = None
    tokenizer = None

bot_name = "MEDAL-AI"

def get_response(sentence, callback):
    # sentence = "do you use credit cards?"
    # sentence = input("You: ")
    # if sentence == "quit":
    #     break
    global model, tokenizer, rag_pipeline
    if not model:
        ret_val = f"{bot_name}: No model loaded. Please load a model first."
        return ret_val
    
    if not model.get_rag_chain():
        model.initialise_rag_chain(rag_pipeline)
    
    response = model.generate(sentence, {}, callback)

    # sentence = tokenize(sentence)
    # X = bag_of_words(sentence, all_words)
    # X = X.reshape(1, X.shape[0])
    # X = torch.from_numpy(X).to(device)

    # output = model(X)
    # _, predicted = torch.max(output, dim=1)

    # tag = tags[predicted.item()]

    # probs = torch.softmax(output, dim=1)
    # prob = probs[0][predicted.item()]
    # if prob.item() > 0.75:
    #     for intent in intents['intents']:
    #         if tag == intent["tag"]:
    #             print(f"{bot_name}: {random.choice(intent['responses'])}")
    # else:
    if response:
        ret_val = f"{response}"
        return ret_val
    print(f"I do not understand...", sentence)
    return "Null"
