from scripts.core import *

class ConfigurationManager:
    def __init__(self, path = nil):
        self.config_path = path if path else "./config.pconf"
        self.config_text = open(self.config_path, "r+")
        self.config = {}

    def change_path(self, new_path):
        self.config_path = new_path
        self.load_config()

    def load_config(self):
        context = nil
        for i in self.config_text.readlines():
            if "[" in i:
                context = i[1:len(i) - 2]
                self.config[context] = {}
                continue
            
            if i not in ['\n', '\t', ' ']:
                endln = 0
                context_value = ""
                context_value_data = ""

                for j in range(len(i)):
                    if i[j] == ' ':
                        endln = j
                        break
                    context_value += i[j]

                for j in range(endln, len(i)):
                    if i[j] == '\n': continue
                    context_value_data += i[j]

                self.config[context][context_value] = context_value_data

    def dump_config(self, head, body, context): ...

    def get_config(self, head, body, dt): return dt(self.config[head][body])
