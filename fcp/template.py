import os
from jinja2 import Template


class Tpl:
    def __init__(self, logger, template_dir):
        self.files = {}

        self.expected_files = [
            "h.jinja",
            "c.jinja",
            "can_ids_h.jinja",
            "can_ids_c.jinja",
            "common_c.jinja",
            "common_h.jinja",
            "enums_h.jinja",
        ]

        self.template_dir = template_dir
        self.tpl = {}

        self.logger = logger
        return

    def check_tpl_dir(self):
        files = os.listdir(self.template_dir)

        for k in self.expected_files:
            if k not in files:
                return False, f"{k} missing"

        return True, ""

    def _get_tpl_dir_files(self):
        files = os.listdir(self.template_dir)
        expand_files = {}

        for k in self.expected_files:
            expand_files[k] = os.path.join(self.template_dir, k)

        return expand_files

    def render(self, name, *args, **kwargs):
        template = self.tpl.get(name)
        if template == None:
            self.logger.error(f"Error: Template not found, {name}")
            return ""

        return template.render(**kwargs)

    def open_tpl_files(self):
        self.files = self._get_tpl_dir_files()

        for k, v in self.files.items():
            try:
                with open(v) as f:
                    self.tpl[k] = Template(f.read())
            except Exception as e:
                self.logger.error(f"Error opening template: {v} not found")
