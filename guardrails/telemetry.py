"""
OpenTelemetry configuration for AI-SecOps-Framework.
Tracks audit performance, validation metrics, and errors.

Usage:
    from guardrails.telemetry import tracer, meter, validation_counter

    with tracer.start_as_current_span("validate_input"):
        validation_counter.add(1, {"result": "valid"})

Requirements:
    pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
"""
import os
import time
from functools import wraps
from typing import Callable, Any

# Try to import OpenTelemetry; fall back to no-op if not installed
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.resources import Resource
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False


def setup_telemetry(service_name: str = "ai-secops-framework"):
    """Initialize OpenTelemetry tracing and metrics.
    
    Args:
        service_name: Name of the service for resource attribution
        
    Returns:
        Tuple of (tracer, meter) instances
    """
    if not OPENTELEMETRY_AVAILABLE:
        return NoOpTracer(), NoOpMeter()
    
    # Resource attributes
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("ENV", "development"),
    })
    
    # Tracing setup
    trace_provider = TracerProvider(resource=resource)
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    
    try:
        otlp_trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
    except Exception:
        # Fall back to no-op if OTLP exporter fails
        pass
    
    trace.set_tracer_provider(trace_provider)
    
    # Metrics setup
    try:
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otlp_endpoint),
            export_interval_millis=30000,  # 30 seconds
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
    except Exception:
        meter_provider = MeterProvider(resource=resource)
        metrics.set_meter_provider(meter_provider)
    
    return trace.get_tracer(__name__), metrics.get_meter(__name__)


class NoOpSpan:
    """No-op span that does nothing."""
    
    def set_attribute(self, key: str, value: Any) -> None:
        """No-op set_attribute."""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class NoOpTracer:
    """No-op tracer when OpenTelemetry is not installed."""
    
    def start_as_current_span(self, name: str, **kwargs):
        """Context manager that returns a no-op span."""
        return NoOpSpan()


class NoOpMeter:
    """No-op meter when OpenTelemetry is not installed."""
    
    def create_counter(self, name: str, description: str = ""):
        """Return a no-op counter."""
        return NoOpCounter()
    
    def create_histogram(self, name: str, description: str = ""):
        """Return a no-op histogram."""
        return NoOpHistogram()


class NoOpCounter:
    """No-op counter that does nothing."""
    
    def add(self, amount: int, attributes: dict = None):
        """No-op add."""
        pass


class NoOpHistogram:
    """No-op histogram that does nothing."""
    
    def record(self, amount: float, attributes: dict = None):
        """No-op record."""
        pass


# Global instances
tracer, meter = setup_telemetry()

# Metrics
validation_counter = meter.create_counter(
    "guardrails.validations.total",
    description="Total number of validation requests"
)

validation_duration = meter.create_histogram(
    "guardrails.validation.duration_ms",
    description="Validation duration in milliseconds"
)

validation_failures = meter.create_counter(
    "guardrails.validations.failed",
    description="Number of failed validations"
)

audit_duration = meter.create_histogram(
    "audit.duration_seconds",
    description="Total audit duration in seconds"
)


def trace_call(span_name: str = None):
    """Decorator to trace function calls with OpenTelemetry.
    
    Args:
        span_name: Name for the span (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or func.__name__
            with tracer.start_as_current_span(name) as span:
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except Exception as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error", str(e))
                    raise
                finally:
                    duration = (time.time() - start) * 1000
                    span.set_attribute("duration_ms", duration)
                    validation_duration.record(duration, {"function": name})
        return wrapper
    return decorator
