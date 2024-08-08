
from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(
   TracerProvider(
       resource=Resource.create({SERVICE_NAME: "billing"})
   )
)
jaeger_exporter = JaegerExporter(
   agent_host_name="jaeger",
   agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
   BatchSpanProcessor(jaeger_exporter)
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route("/")
def pay():
    with trace.get_tracer(__name__).start_as_current_span("pay"):
        res = requests.get("http://order:8002")
        return "Payed"+" "+res.text