import re
from functools import partial

import numpy as np
import torch
import os
from modules.callbacks import Iteratorize
from langchain.vectorstores.neo4j_vector import Neo4jVector
# from langchain.embeddings.
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from langchain.chains import RetrievalQA
from huggingface_hub.hf_api import HfFolder

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from schemas.rag import KGRag

try:
    import llama_cpp
except:
    llama_cpp = None

try:
    import llama_cpp_cuda
except:
    llama_cpp_cuda = None

try:
    import llama_cpp_cuda_tensorcores
except:
    llama_cpp_cuda_tensorcores = None

token = "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"

HfFolder.save_token(token)

URI = "neo4j://192.168.0.115:7687"
AUTH = ("neo4j", "password")

def llama_cpp_lib():
    # if shared.args.cpu and llama_cpp is not None:
    #     return llama_cpp
    # elif shared.args.tensorcores and llama_cpp_cuda_tensorcores is not None:
    #     return llama_cpp_cuda_tensorcores
    if llama_cpp_cuda is not None:
        return llama_cpp_cuda
    else:
        return llama_cpp


def ban_eos_logits_processor(eos_token, input_ids, logits):
    logits[eos_token] = -float('inf')
    return logits


def custom_token_ban_logits_processor(token_ids, input_ids, logits):
    for token_id in token_ids:
        logits[token_id] = -float('inf')

    return logits


class LlamaCppModel:
    def __init__(self):
        self.initialized = False
        self.grammar_string = ''
        self.grammar = None
        self.rag_chain = None

    def __del__(self):
        del self.model

    @classmethod
    def from_pretrained(self, path):

        Llama = llama_cpp_lib().Llama
        LlamaCache = llama_cpp_lib().LlamaCache

        result = self()
        cache_capacity = 0
        # if shared.args.cache_capacity is not None:
        #     if 'GiB' in shared.args.cache_capacity:
        #         cache_capacity = int(re.sub('[a-zA-Z]', '', shared.args.cache_capacity)) * 1000 * 1000 * 1000
        #     elif 'MiB' in shared.args.cache_capacity:
        #         cache_capacity = int(re.sub('[a-zA-Z]', '', shared.args.cache_capacity)) * 1000 * 1000
        #     else:
        #         cache_capacity = int(shared.args.cache_capacity)

        # if cache_capacity > 0:
        #     logger.info("Cache capacity is " + str(cache_capacity) + " bytes")

        # if shared.args.tensor_split is None or shared.args.tensor_split.strip() == '':
        #     tensor_split_list = None
        # else:
        #     tensor_split_list = [float(x) for x in shared.args.tensor_split.strip().split(",")]

        params = {
            'model_path': str(path),
            'n_ctx': 4096*4,
            'n_threads': 8,
            'n_threads_batch': None,
            'n_batch': 512,
            'use_mmap': True,
            'use_mlock': False,
            'mul_mat_q': True,
            'numa': False,
            'n_gpu_layers': 256,
            'rope_freq_base': 500000,
            'rope_freq_scale': 1.0,
            'offload_kqv': True,
            'split_mode': 2
        }

        result.model = Llama(**params)
        if cache_capacity > 0:
            result.model.set_cache(LlamaCache(capacity_bytes=cache_capacity))

        # result.initialise_vector_indexes()
        # result.setup_rag_pipeline()
        # This is ugly, but the model and the tokenizer are the same object in this library.
        return result, result

    

    

    def encode(self, string):
        if type(string) is str:
            string = string.encode()

        return self.model.tokenize(string)

    def decode(self, ids, **kwargs):
        return self.model.detokenize(ids).decode('utf-8')

    def get_logits(self, tokens):
        self.model.reset()
        self.model.eval(tokens)
        logits = self.model._scores
        logits = np.expand_dims(logits, 0)  # batch dim is expected
        return torch.tensor(logits, dtype=torch.float32)

    def load_grammar(self, string):
        if string != self.grammar_string:
            self.grammar_string = string
            if string.strip() != '':
                self.grammar = llama_cpp_lib().LlamaGrammar.from_string(string)
            else:
                self.grammar = None

    def get_rag_chain(self):
        return self.rag_chain

    def initialise_rag_chain(self, rag_pipeline: KGRag):
        if not rag_pipeline.get_rag_chain():
            rag_pipeline.setup_rag_pipeline()
        
        self.rag_chain = rag_pipeline.get_rag_chain()


    def generate(self, prompt, state, callback=None):
        print("LOLOLOLOLOL -----------------------", prompt)
        LogitsProcessorList = llama_cpp_lib().LogitsProcessorList
        prompt = prompt if type(prompt) is str else prompt.decode()

        # Handle truncation
        prompt = self.encode(prompt)
        prompt = prompt[-10000:]
        prompt = self.decode(prompt)

        self.load_grammar("")
        logit_processors = LogitsProcessorList()
        # if state['ban_eos_token']:
        #     logit_processors.append(partial(ban_eos_logits_processor, self.model.token_eos()))

        # if state['custom_token_bans']:
        #     to_ban = [int(x) for x in state['custom_token_bans'].split(',')]
        #     if len(to_ban) > 0:
        #         logit_processors.append(partial(custom_token_ban_logits_processor, to_ban))

        # completion_chunks = self.model.create_completion(
        #     prompt=prompt,
        #     max_tokens=state['max_new_tokens'],
        #     temperature=state['temperature'],
        #     top_p=state['top_p'],
        #     min_p=state['min_p'],
        #     typical_p=state['typical_p'],
        #     frequency_penalty=state['frequency_penalty'],
        #     presence_penalty=state['presence_penalty'],
        #     repeat_penalty=state['repetition_penalty'],
        #     top_k=state['top_k'],
        #     stream=True,
        #     seed=int(state['seed']) if state['seed'] != -1 else None,
        #     tfs_z=state['tfs'],
        #     mirostat_mode=int(state['mirostat_mode']),
        #     mirostat_tau=state['mirostat_tau'],
        #     mirostat_eta=state['mirostat_eta'],
        #     logits_processor=logit_processors,
        #     grammar=self.grammar
        # )
            
        print("################################ only the prompt -> ", prompt)
        completion_chunks = self.rag_chain.invoke(
            {
            "question": prompt,
            "chat_history": []
        }
        )

        output = ""
        for completion_chunk in completion_chunks:

            delta = completion_chunk["choices"][0]["delta"]
            # print("output text: ", text)
            text = ""
            if "content" in delta:
                text = delta["content"]
            
            output += text
            if callback:
                callback(text)

        return output

    def generate_with_streaming(self, *args, **kwargs):
        print("LOLOLOLOLOL")
        with Iteratorize(self.generate, args, kwargs, callback=None) as generator:
            reply = ''
            for token in generator:
                reply += token
                yield reply
