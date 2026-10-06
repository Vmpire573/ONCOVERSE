"""Optional bounded Kafka JSON event consumer."""
import csv,json,os,tempfile
from pathlib import Path
from .etl import REQUIRED,ingest_csv
def consume_kafka(topic,brokers=None,max_messages=100):
    try: from kafka import KafkaConsumer
    except ImportError as exc: raise RuntimeError("Install optional Kafka support: pip install -r requirements-optional.txt") from exc
    consumer=KafkaConsumer(topic,bootstrap_servers=(brokers or os.getenv("KAFKA_BOOTSTRAP_SERVERS","127.0.0.1:9092")).split(","),value_deserializer=lambda b:json.loads(b.decode()),consumer_timeout_ms=5000,auto_offset_reset="earliest",enable_auto_commit=False,group_id="oncoverse-academic")
    batch=[]
    try:
        for message in consumer:
            batch.append(message.value)
            if len(batch)>=max_messages: break
        if not batch:return {"topic":topic,"received":0,"accepted":0,"rejected":0}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"batch.csv"
            with path.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=REQUIRED+(["site_code"] if any("site_code" in row for row in batch) else []),extrasaction="ignore");writer.writeheader();writer.writerows(batch)
            result=ingest_csv(str(path),source_name=f"kafka:{topic}")
        consumer.commit()
        return result
    finally: consumer.close()
