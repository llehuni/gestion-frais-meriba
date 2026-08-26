"""
Middleware pour journaliser les opérations sensibles via AuditLog
et capturer IP/user_agent. Stocke request en thread-local pour signaux.
"""
import threading

_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, "request", None)

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
