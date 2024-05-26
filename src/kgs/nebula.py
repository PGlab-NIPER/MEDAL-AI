import json
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from kgs.knowledge_graph import KnowledgeGraph

class NebulaGraph(KnowledgeGraph):
    def __init__(self, space, username, password, address, port, session_pool_size):
        self.space = space
        self.username = username
        self.password = password
        self.address = address
        self.port = port
        self.session_pool_size = session_pool_size
        self.session = self.get_session()
        self.client = self.get_client()
        
        # Nebula Graph connection configuration
        config = Config()
        config.max_connection_pool_size = 10
        self.connection_pool = ConnectionPool()
        self.connection_pool.init([('192.168.0.115', 9669)], config)

        # Create a session to execute queries
        session = self.connection_pool.get_session('root', 'nebula')
    
    def load_config(self):
        # load config from file
        config = json.load(open('nebula_config.json'))

    def get_session(self):
        return self.connection_pool.get_session(self.username, self.password)

    def query(self, query):
        return self.session.execute(query)

    def create_node(self, label, properties):
        return self.session.execute(
            f"INSERT VERTEX {label} {self._format_properties(properties)}")

    def create_relationship(self, start_node, end_node, relationship, properties):
        return self.session.execute(
            f"INSERT EDGE {relationship} {self._format_properties(properties)}")

    def _format_properties(self, properties):
        return "{" + ",".join([f"{key}: '{value}'" for key, value in properties.items()]) + "}"
    
    def get_schema(self):
        return self.session.execute("SHOW TAGS; SHOW EDGES;")
    
    
    