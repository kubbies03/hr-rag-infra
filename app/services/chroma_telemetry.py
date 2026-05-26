"""Local Chroma telemetry override for quiet demo and deploy logs."""

from chromadb.telemetry.product import ProductTelemetryClient, ProductTelemetryEvent
from overrides import override


class NoOpProductTelemetryClient(ProductTelemetryClient):
    """Disable Chroma product telemetry by dropping all events."""

    @override
    def capture(self, event: ProductTelemetryEvent) -> None:
        return None
