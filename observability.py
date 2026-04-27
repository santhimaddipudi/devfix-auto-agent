import os

langfuse = None
_CallbackHandler = None

try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler as _CallbackHandler

    _secret = os.getenv("LANGFUSE_SECRET_KEY")
    _public = os.getenv("LANGFUSE_PUBLIC_KEY")
    if _secret and _public:
        langfuse = Langfuse(
            secret_key=_secret,
            public_key=_public,
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
except ImportError:
    pass


def get_tracer():
    if _CallbackHandler and os.getenv("LANGFUSE_PUBLIC_KEY"):
        return _CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
    return None


def log_metric(trace_id, metric_name, value):
    if langfuse and trace_id:
        langfuse.score(trace_id=trace_id, name=metric_name, value=value)
