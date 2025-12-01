class NoCacheMiddleware:
    """Middleware that adds no-cache headers for authenticated HTML responses.

    This prevents browsers from serving protected pages from cache after logout
    when the user presses the back button.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            user = getattr(request, "user", None)
            content_type = response.get("Content-Type", "")

            # Only modify HTML responses and only when a user was authenticated
            if user and getattr(user, "is_authenticated", False) and "text/html" in content_type:
                response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response["Pragma"] = "no-cache"
                response["Expires"] = "0"
        except Exception:
            # Fail-safe: don't break the response in case of unexpected issues
            pass

        return response
