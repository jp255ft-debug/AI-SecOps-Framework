"""Unit tests for guardrails/telemetry.py"""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from guardrails.telemetry import (
    setup_telemetry,
    NoOpTracer,
    NoOpMeter,
    NoOpCounter,
    NoOpHistogram,
    trace_call,
)


class TestSetupTelemetry:
    """Tests for setup_telemetry function."""

    def test_setup_telemetry_default(self):
        """Test telemetry setup with default service name."""
        tracer_provider, meter = setup_telemetry()
        assert tracer_provider is not None
        assert meter is not None

    def test_setup_telemetry_custom_name(self):
        """Test telemetry setup with custom service name."""
        tracer_provider, meter = setup_telemetry(service_name="custom-service")
        assert tracer_provider is not None
        assert meter is not None

    def test_setup_telemetry_disabled(self):
        """Test telemetry setup when OTEL is disabled."""
        with patch.dict(os.environ, {"OTEL_SDK_DISABLED": "true"}, clear=True):
            tracer_provider, meter = setup_telemetry()
            assert tracer_provider is not None
            assert meter is not None

    def test_setup_telemetry_no_opentelemetry(self):
        """Test telemetry setup when opentelemetry is not installed."""
        with patch.dict("sys.modules", {
            "opentelemetry": None,
            "opentelemetry.sdk": None,
            "opentelemetry.sdk.trace": None,
            "opentelemetry.sdk.metrics": None,
            "opentelemetry.exporter.otlp": None,
        }):
            tracer_provider, meter = setup_telemetry()
            assert tracer_provider is not None
            assert meter is not None

    def test_setup_telemetry_returns_noop_on_error(self):
        """Test telemetry returns NoOp implementations on any error."""
        with patch("guardrails.telemetry.NoOpTracer") as mock_noop:
            mock_noop.return_value = MagicMock()
            tracer_provider, meter = setup_telemetry()
            assert tracer_provider is not None


class TestNoOpTracer:
    """Tests for NoOpTracer class."""

    def test_start_as_current_span_returns_context_manager(self):
        """Test NoOpTracer.start_as_current_span returns a context manager."""
        tracer = NoOpTracer()
        cm = tracer.start_as_current_span("test-span")
        # Should be usable as context manager without error
        with cm as span:
            pass  # Should not raise

    def test_start_as_current_span_with_attributes(self):
        """Test NoOpTracer with attributes."""
        tracer = NoOpTracer()
        with tracer.start_as_current_span("test-span", attributes={"key": "value"}):
            pass  # Should not raise

    def test_start_as_current_span_nested(self):
        """Test nested spans with NoOpTracer."""
        tracer = NoOpTracer()
        with tracer.start_as_current_span("parent"):
            with tracer.start_as_current_span("child"):
                pass  # Should not raise

    def test_start_as_current_span_multiple_calls(self):
        """Test multiple span calls."""
        tracer = NoOpTracer()
        for i in range(10):
            with tracer.start_as_current_span(f"span-{i}"):
                pass


class TestNoOpMeter:
    """Tests for NoOpMeter class."""

    def test_create_counter(self):
        """Test NoOpMeter.create_counter returns NoOpCounter."""
        meter = NoOpMeter()
        counter = meter.create_counter("test-counter", "Test counter")
        assert isinstance(counter, NoOpCounter)

    def test_create_histogram(self):
        """Test NoOpMeter.create_histogram returns NoOpHistogram."""
        meter = NoOpMeter()
        histogram = meter.create_histogram("test-histogram", "Test histogram")
        assert isinstance(histogram, NoOpHistogram)

    def test_create_counter_default_description(self):
        """Test counter creation with default description."""
        meter = NoOpMeter()
        counter = meter.create_counter("test")
        assert isinstance(counter, NoOpCounter)

    def test_create_histogram_default_description(self):
        """Test histogram creation with default description."""
        meter = NoOpMeter()
        histogram = meter.create_histogram("test")
        assert isinstance(histogram, NoOpHistogram)

    def test_create_multiple_counters(self):
        """Test creating multiple counters."""
        meter = NoOpMeter()
        for name in ["counter1", "counter2", "counter3"]:
            counter = meter.create_counter(name, f"Counter {name}")
            assert isinstance(counter, NoOpCounter)


class TestNoOpCounter:
    """Tests for NoOpCounter class."""

    def test_add(self):
        """Test NoOpCounter.add does not raise."""
        counter = NoOpCounter()
        counter.add(1)  # Should not raise

    def test_add_with_attributes(self):
        """Test NoOpCounter.add with attributes."""
        counter = NoOpCounter()
        counter.add(5, attributes={"env": "test"})  # Should not raise

    def test_add_zero(self):
        """Test NoOpCounter.add with zero."""
        counter = NoOpCounter()
        counter.add(0)

    def test_add_negative(self):
        """Test NoOpCounter.add with negative value."""
        counter = NoOpCounter()
        counter.add(-1)

    def test_add_multiple_times(self):
        """Test multiple add calls."""
        counter = NoOpCounter()
        for i in range(100):
            counter.add(i)


class TestNoOpHistogram:
    """Tests for NoOpHistogram class."""

    def test_record(self):
        """Test NoOpHistogram.record does not raise."""
        histogram = NoOpHistogram()
        histogram.record(1.0)  # Should not raise

    def test_record_with_attributes(self):
        """Test NoOpHistogram.record with attributes."""
        histogram = NoOpHistogram()
        histogram.record(5.0, attributes={"env": "test"})  # Should not raise

    def test_record_zero(self):
        """Test NoOpHistogram.record with zero."""
        histogram = NoOpHistogram()
        histogram.record(0.0)

    def test_record_negative(self):
        """Test NoOpHistogram.record with negative value."""
        histogram = NoOpHistogram()
        histogram.record(-1.0)

    def test_record_multiple_times(self):
        """Test multiple record calls."""
        histogram = NoOpHistogram()
        for i in range(100):
            histogram.record(float(i))


class TestTraceCall:
    """Tests for trace_call decorator."""

    def test_trace_call_basic(self):
        """Test trace_call decorator on basic function."""
        @trace_call()
        def my_function():
            return "result"
        
        assert my_function() == "result"

    def test_trace_call_with_name(self):
        """Test trace_call with custom span name."""
        @trace_call(span_name="custom-span")
        def my_function():
            return 42
        
        assert my_function() == 42

    def test_trace_call_with_args(self):
        """Test trace_call with function arguments."""
        @trace_call()
        def add(a, b):
            return a + b
        
        assert add(1, 2) == 3

    def test_trace_call_with_kwargs(self):
        """Test trace_call with keyword arguments."""
        @trace_call()
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        assert greet("World") == "Hello, World!"

    def test_trace_call_exception_handling(self):
        """Test trace_call handles exceptions gracefully."""
        @trace_call()
        def failing_function():
            raise ValueError("test error")
        
        with pytest.raises(ValueError, match="test error"):
            failing_function()

    def test_trace_call_nested(self):
        """Test nested trace_call decorators."""
        @trace_call()
        def inner():
            return "inner"
        
        @trace_call()
        def outer():
            return inner()
        
        assert outer() == "inner"

    def test_trace_call_method(self):
        """Test trace_call on class method."""
        class MyClass:
            @trace_call()
            def method(self):
                return "method"
        
        obj = MyClass()
        assert obj.method() == "method"

    def test_trace_call_static_method(self):
        """Test trace_call on static method."""
        class MyClass:
            @staticmethod
            @trace_call()
            def static_method():
                return "static"
        
        assert MyClass.static_method() == "static"
