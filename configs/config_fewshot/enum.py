import yaml

class LoadConfig:
    def __init__(self):
        YAML_PATH = "configs/config_fewshot/example_fewshot.yml"
        with open(YAML_PATH, 'r') as cfg:
            self.app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        
        self.load_example_fewshot()
        self.load_seach_config()


    def load_seach_config(self):
        self.elastic_url = self.app_config['search_config']['elastic_url']
        self.num_size_elas = self.app_config['search_config']['num_size_elas']
        self.index_name = self.app_config['search_config']['index_name']
        self.quantity_specifications = self.app_config['search_config']['quantity_specifications']
        self.chep_keywords = self.app_config['search_config']['chep_keywords']
        self.expensive_keywords = self.app_config['search_config']['expensive_keywords']

    def load_example_fewshot(self):
        self.example_price = self.app_config['example_price']
        self.example_power = self.app_config['example_power']
        self.example_volume = self.app_config['example_volume']
        self.example_weight = self.app_config['example_weight']
        self.example_quantity = self.app_config['example_quantity']

ELASTICH_SEARCH_CONFIG = LoadConfig()