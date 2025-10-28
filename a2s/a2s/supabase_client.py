from supabase import create_client
from django.conf import settings

# Use service key here, so all views get full access
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
