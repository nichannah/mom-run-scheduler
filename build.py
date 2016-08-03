import os

class Build:
    def __init__(self, ws_dir, model, build_type, compiler):
        # Build is DEBUG, REPRO, OPT etc.
        self.ws_dir = ws_dir
        self.model = model
        self.build_type = build_type
        self.compiler = compiler
        self.name = build_type + '_' + compiler

        self.build_dir = os.path.join(ws_dir, 'exec', 'nci', model.name)
        self.exe = os.path.join(self.build_dir, 'fms_' + model.name + '.x')

    def build(self):
        if not os.path.exists(self.exe):
            return self.model.build(self.build_type, self.compiler)
        else:
            return 0

