import json
from django.core.management.base import BaseCommand
from a2s_system.models import Curriculum

class Command(BaseCommand):
    help = "Import a curriculum JSON file into the Curriculum model"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Path to curriculum.json or folder')

    def handle(self, *args, **options):
        path = options['file']
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)

        # If your JSON contains top-level {"program": "...", "curriculum": [...]} then use that
        program = payload.get("program") or payload.get("program_name") or input("Program name: ")
        # Store the whole payload so front-end can read same structure
        Curriculum.objects.update_or_create(program=program, defaults={"data": payload})
        self.stdout.write(self.style.SUCCESS(f"Imported curriculum for {program}"))
