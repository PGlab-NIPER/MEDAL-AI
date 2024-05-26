from neo4j import GraphDatabase
from langchain.vectorstores.neo4j_vector import Neo4jVector
# from langchain.embeddings.
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from kgs.knowledge_graph import KnowledgeGraph
import csv

class Neo4jKG(KnowledgeGraph):
    database = None
    def __init__(self, uri, user, password):
        super().__init__(uri, user, password)
        self.vector_indexes = {}
        self.database = None

    def create_node(self, label, properties):
        return super().create_node(label, properties)

    def create_relationship(self, start_node, end_node, relationship, properties):
        return super().create_relationship(start_node, end_node, relationship, properties)

    def query(self, query):
        return super().query(query)
    
    def get_graph_driver(self, uri, user, password):
        return GraphDatabase.driver(uri, auth=(user, password))
    
    def initialise_vector_indexes(self):
        em = HuggingFaceEmbeddings(model_name='BAAI/bge-large-en-v1.5')

        if not self.database:
            self.setup_for_medkg(em)
        else:
            if self.database == 'primekg':
                self.setup_for_primekg(em)
            else:
                self.setup_for_medkg(em)

    def setup_for_primekg(self, embedding_model):
        self.vector_index = Neo4jVector.from_existing_graph(
            embedding_model,
            url=self.uri,
            username="neo4j",
            password="password",
            index_name='Protein',
            keyword_index_name='protein_name',
            node_label="protein",
            text_node_properties=['name', 'description', 'source'],
            embedding_node_property='embedding',
            search_type='hybrid',
        )

        self.vector_index2 = Neo4jVector.from_existing_graph(
            embedding_model,
            url=self.uri,
            username="neo4j",
            password="password",
            index_name='Drug',
            keyword_index_name='drug_description',
            node_label="drug",
            text_node_properties=['name','description', 'half_life', 'indication', 'mechanism_of_action', 'protein_binding', 'pharmacodynamics', 'state', 'atc_1', 'atc_2', 'atc_3', 'atc_4',
                'category', 'group', 'pathway', 'molecular_weight', 'tpsa', 'clogp'],
            embedding_node_property='embedding',
            search_type='hybrid'
        )

        self.vector_index3 = Neo4jVector.from_existing_graph(
            embedding_model,
            url=self.uri,
            username="neo4j",
            password="password",
            index_name='Disease',
            keyword_index_name='disease_description',
            node_label="disease",
            text_node_properties=['mondo_name', 'mondo_definition', 'umls_description', 'orphanet_definition', 'orphanet_prevalence', 'orphanet_epidemiology', 'orphanet_clinical_description', 'orphanet_management_and_treatment', 'mayo_symptoms', 'mayo_causes', 'mayo_risk_factors', 'mayo_complications', 'mayo_prevention', 'mayo_see_doc'],
            embedding_node_property='embedding',
            search_type='hybrid'
        )

    def setup_for_medkg(self, embedding_model):
        retrieval_query = """
            with node, score, 
            collect {
                match (node)-[e]-(d:Disease) with e, d limit 2 
                return {
                            interaction_type: type(e),
                            name: d.name,
                            short_description: d.description
                        }
                } as dd, 
            collect{
                match (node)-[e]-(d:Protein) with e, d limit 5
                return {
                            interaction_type: type(e),
                            name: d.name,
                            accession: d.accession,
                            synonyms: d.synonyms_str
                        }
                } as dp1, 
            collect{
                match (node)-[e]-(d:Metabolite) with e, d limit 5
                return {
                            interaction_type: type(e),
                            name: d.name,
                            short_description: d.description,
                            chemical_formula: d.chemical_formula,
                            synonyms: d.synonyms
                        }
                } as dmeta, 
            collect{
                match (node)-[e]-(d:Clinically_relevant_variant) with e, d limit 5
                return {
                            interaction_type: type(e),
                            name: "chromosome " + d.chromosome,
                            alternative_names: d.alternative_names
                        }
                }  as dcrv, 
            collect{
                match (node)-[e]-(d:Experimental_factor) with e, d limit 2
                return {
                            interaction_type: type(e),
                            name: d.name,
                            short_description: d.description
                        }
                } as def, 
            collect{
                match (node)-[e]-(d:Publication) with e, d limit 5
                return {
                            interaction_type: type(e),
                            publication_link: d.linkout,
                            PMID: d.id,
                            PMC_ID: d.PMC_id
                        }
                } as dp2
            return 
            node {
                details:{
                    name: node.name,
                    type: apoc.text.join(labels(node), ","),
                    description: node.full_description
                },
                disease_interaction: dd,
                protein_interaction: dp1,
                metabolite_interaction: dmeta,
                clinically_relevant_variant_interaction: dcrv,
                experimental_factor_interaction: def,
                publications: dp2
            } as text, score , node{.type} as metadata
        """
        self.vector_indexes['disease'] = Neo4jVector.from_existing_graph(
            embedding_model,
            url=self.uri,
            username="neo4j",
            password="password",
            index_name='Disease',
            keyword_index_name='disease_index',
            node_label="Disease",
            text_node_properties=['name', 'full_description', 'synonyms_str'],
            embedding_node_property='embedding',
            search_type='hybrid',
            retrieval_query=retrieval_query
        )
    
    def get_retreiver(self):

        retreiver = self.vector_indexes['disease'].as_retriever(
            search_type = "similarity_score_threshold",
            search_kwargs = {"k":3, 'score_threshold': 0.99}
        )

        return retreiver
