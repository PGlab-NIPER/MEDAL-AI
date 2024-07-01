from enum import Enum
from langchain.vectorstores.neo4j_vector import Neo4jVector
# from langchain.embeddings.
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from langchain.chains import RetrievalQA
from kgs.nebula import NebulaGraph
from kgs.neo4j import Neo4jKG
from langchain_core.runnables import (ConfigurableField, Runnable,
                                      RunnableConfig, RunnableParallel,
                                      RunnablePassthrough,
                                      RunnableSerializable, ensure_config)
# from llama_index.llms.llama_utils import messages_to_prompt, completion_to_prompt


URI = "neo4j://localhost:7690"
AUTH = ("neo4j", "password")

class Rag:
    rag_chain = None
    model = None
    def __init__(self, model):
        self.model = model.model
        return
    
    def load_rag_configs():
        return
    
class KGRag(Rag):
    # Define clas variable with constraints
    class KGProvider(Enum):
        NEBULA = 'nebula'
        ARANGO = 'arango'
        NEO4j = 'neo4j'

    kg_provider_name = KGProvider.NEO4j
    kg_provider = None
    
    

    def __init__(self, kg_type, model):
        super().__init__(model)
        if kg_type == 'nebula':
            self.kg_provider_name = self.KGProvider.NEBULA
            self.kg_provider = NebulaGraph(URI, AUTH)
        # elif kg_type == 'arango':
        #     self.kg_provider_name = self.KGProvider.ARANGO
        elif kg_type == 'neo4j':
            self.kg_provider_name = self.KGProvider.NEO4j
            self.kg_provider = Neo4jKG(URI, AUTH[0], AUTH[1])

    def initialise_vector_indexes(self):
        if self.kg_provider_name == self.KGProvider.NEBULA:
            em = HuggingFaceEmbeddings(model_name='BAAI/bge-large-en-v1.5')
            
            
        # elif self.kg_provider_name == self.KGProvider.ARANGO:
        #     em = HuggingFaceEmbeddings(model_name='BAAI/bge-large-en-v1.5')
        #     self.vector_index = ArangoVector.from_existing_graph(
        #         em,
        #         url="")
        elif self.kg_provider_name == self.KGProvider.NEO4j:
            self.kg_provider.initialise_vector_indexes()
    
    def load_rag_configs():
        return
    
    def setup_rag_pipeline(self):
        # In your responses do not mention or refer to the context like ```According to the provided information```, ```From the provided context``` etc, just use it to answer the question.
        cq = """You are a medical chat assistant who answers user queries lieka professional Medical Expert.
            Use the context provided to help answer the user queries.
            Keep the response precise and include all the requested information. Do not apologise or repeat responses. 
            In case you dont know the answer or cannot find anything in the context, Say `Apologies, I do not know the answer to this query.`

            Context: {context}
        """

        def get_chat_template(question):
            cqq = cq.format(context=question["context"])
            print("context: ", question["context"])
            return [
                { "role": "system", "content": cqq},
                { "role": "user", "content": question['question']}
            ]

        def generate_with_configs(input):
            print("input: ", input)
            return self.model.create_chat_completion(input,
                max_tokens=4096,
                temperature=0.6,
                top_p=0.1,
                min_p=0.5,
                typical_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                repeat_penalty=1.18,
                top_k=40,
                stream=True,
                seed=-1,
                tfs_z=1,
                mirostat_mode=0,
                mirostat_tau=1,
                mirostat_eta=0.1,
            )
    
        # contextualize_q_chain = get_chat_template | generate_with_configs | StrOutputParser()

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)


        def contextualized_question(input: dict):
            return input["question"]
            if input.get("chat_history"):
                return contextualize_q_chain
            else:
                return input["question"]

        retreiver = self.kg_provider.get_retreiver()

        self.rag_chain = (
            RunnablePassthrough.assign(
                context = contextualized_question | retreiver | format_docs
            )
            | get_chat_template 
            | generate_with_configs
        )
        

        # self.rag_chain = self.kg_provider.get_chain()


    def get_rag_chain(self):
        return self.rag_chain


    # @deprecated
    def evaluate_using_rag(self, file_path):
        # cq = """You are a medical chat assistant who answers user queries based on the context provided. The context will be provided as a knowledge graph where details will contain the information on the fetched data and then corresponsing interactions with other nodes. 
        #     Keep the response precise and include all the requested information. Do not apologise or repeat responses. 
        #     In case you dont know the answer, Say `Apologies, I do not know the answer to this query.`

        #     Context: {context}
        # """

        i = 0
        correct = 0
        incorrect = 0

        

        def generate_with_configs(input):
            return self.model.create_chat_completion(input,
                max_tokens=4096,
                temperature=0.9,
                top_p=0.1,
                min_p=0.5,
                typical_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                repeat_penalty=1.18,
                top_k=40,
                stream=True,
                seed=-1,
                tfs_z=1,
                mirostat_mode=0,
                mirostat_tau=1,
                mirostat_eta=0.1,
            )
    
        # contextualize_q_chain = get_chat_template | generate_with_configs | StrOutputParser()

        def contextualized_question(input: dict):
            return input["question"]
            if input.get("chat_history"):
                return contextualize_q_chain
            else:
                return input["question"]

        dataset = self.load_data_for_evaluation(file_path)
        flog = open('logs.txt', 'w')
        for key, value in dataset.items():
            i+=1

            cq = """
                Based on the given context asnwer the given question in wither a `yes`, `no` or `maybe` response.

                Context: {context}
            """

            def get_chat_template(question):
                context = " ".join(value['CONTEXTS']) # + "\n\n\n" + question["context"]
                cqq = cq.format(context=context)
                return [
                    { "role": "system", "content": cqq},
                    { "role": "user", "content": question}
                ]

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)


            # retreiver = self.kg_provider.get_retreiver()

            # self.rag_chain = (
            #     RunnablePassthrough.assign(
            #         context = contextualized_question | retreiver | format_docs
            #     )
            #     | get_chat_template 
            #     | generate_with_configs
            # )

            completion_chunks = generate_with_configs(get_chat_template(value["QUESTION"]))

            # completion_chunks = self.rag_chain.invoke(
            #     {
            #     "question": value["QUESTION"],
            #     "chat_history": []
            # }
            # )

            output = ""
            for completion_chunk in completion_chunks:

                delta = completion_chunk["choices"][0]["delta"]
                # print("output text: ", text)
                text = ""
                if "content" in delta:
                    text = delta["content"]
                
                output += text

            if value['final_decision'].lower() == output.lower():
                correct += 1
                r = f"key: {key} - Answer: {value['final_decision']} - Correct Answer: {output} {correct/i} {correct} {i}"
                print(r)
            else:
                incorrect += 1
                r = f"key: {key} - Answer: {value['final_decision']} - Incorrect Answer: {output} {incorrect/i} {incorrect} {i}"
                print(r)
            flog.write(r + "\n")

            # return output

    def load_data_for_evaluation(self, file_path):
        import json
        f = open(file_path, 'r')
        json_data = json.load(f)
        f.close()

        return json_data
