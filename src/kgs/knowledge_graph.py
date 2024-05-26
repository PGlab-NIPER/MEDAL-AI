class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = self.get_graph_driver(uri, user, password)
        self.uri = uri

    def get_graph_driver(self, uri, user, password):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def query(self, query):
        raise NotImplementedError

    def create_node(self, label, properties):
        raise NotImplementedError

    def create_relationship(self, start_node, end_node, relationship, properties):
        raise NotImplementedError

    def get_retreiver(self):
        raise NotImplementedError
