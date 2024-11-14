import uuid
import json
import time
from kafka import KafkaProducer, KafkaConsumer
from PIL import Image
import base64
import pickle
import numpy as np
from io import BytesIO
import random
import threading
from datetime import datetime
import matplotlib.pyplot as plt
import os

# Kafka Producer ID for tracking purposes
producer_id = os.environ.get('PRODUCER_ID', 'default-producer')  # 设置默认值为字符串
print(f"Producer ID is {producer_id}")

# Latency list to record all message latencies
latency_list = []

# File path for saving latency data
latency_file_path = f"latency_data_{producer_id}.txt"

# Flag to track when to stop the consumer
all_messages_received = threading.Event()

# Number of messages to send
NUM_MESSAGES = 1000

# Initialize Kafka producer
try:
    producer = KafkaProducer(
        bootstrap_servers='192.168.5.142:30092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks=1,
        api_version=(0, 10, 1)
    )
    print(f"Kafka producer initialized successfully with ID {producer_id}.")
except Exception as e:
    print(f"Failed to initialize Kafka producer: {e}")

sent_images = {}

def inference_consumer():
    messages_received = 0
    try:
        consumer = KafkaConsumer(
            'time-topic',
            bootstrap_servers='192.168.5.142:30092',
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=f'inference-consumer-group-{producer_id}',  # 使用字符串 producer_id
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        print("Kafka consumer started, listening for inference results.")
        
        with open(latency_file_path, 'a') as latency_file:
            for message in consumer:
                data = message.value  
                print(f"Received inference result: {data}")

                result_producer_id = data.get('producer_id', None)
                if result_producer_id is None:
                    print("Missing producer_id in the received message!")
                    continue  

                if result_producer_id == producer_id:  # 匹配字符串 producer_id
                    result_id = data['ID']  
                    original_data = sent_images[result_id]
                    sent_time = original_data['SentTime']

                    received_time = datetime.now()
                    latency = (received_time - sent_time).total_seconds()

                    # Record the latency for each message
                    latency_list.append(latency)
                    latency_file.write(f"{latency}\n")  # Write latency to file
                    messages_received += 1

                    print(f"Inference completed for producer {producer_id}, ID {result_id}")
                    print(f"End-to-end latency for ID {result_id}: {latency:.4f} seconds")

                    # Check if all messages are received
                    if messages_received >= NUM_MESSAGES:
                        all_messages_received.set()  # Signal that all messages are received
                        break  # Stop consuming further messages
                
    except Exception as e:
        print(f"Error in Kafka inference consumer: {e}")

# Start a separate thread for the Kafka consumer
consumer_thread = threading.Thread(target=inference_consumer)
consumer_thread.start()

# Load CIFAR-10 dataset from local path
cifar10_path = './cifar-10-batches-py/'

def unpickle(file):
    try:
        with open(file, 'rb') as fo:
            data_dict = pickle.load(fo, encoding='bytes')
        print(f"Successfully loaded CIFAR-10 data: {file}")
        return data_dict
    except Exception as e:
        print(f"Error loading CIFAR-10 data: {e}")

def load_label_names():
    try:
        with open(cifar10_path + 'batches.meta', 'rb') as f:
            label_data = pickle.load(f, encoding='bytes')
        label_names = [label.decode('utf-8') for label in label_data[b'label_names']]
        print(f"Successfully loaded label names: {label_names}")
        return label_names
    except Exception as e:
        print(f"Error loading label names: {e}")
        return []

label_names = load_label_names()
batch = unpickle(cifar10_path + 'data_batch_1')
images = batch[b'data']
labels = batch[b'labels']

def convert_image(image_data):
    try:
        image_data = np.reshape(image_data, (3, 32, 32)).transpose(1, 2, 0)
        image = Image.fromarray(image_data)
        print("Image conversion successful.")
        return image
    except Exception as e:
        print(f"Error converting image: {e}")

def send_image_to_kafka(image_data, label):
    try:
        unique_id = str(uuid.uuid4())
        print(f"Generated unique ID: {unique_id}")

        image = convert_image(image_data)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        print("Image successfully converted to base64.")

        data = {
            'ID': unique_id,
            'GroundTruth': label,
            'Data': img_str,
            'producer_id': producer_id  # 使用字符串 producer_id
        }

        sent_images[unique_id] = {'GroundTruth': label, 'SentTime': datetime.now()}

        producer.send('iot-topic', value=data)
        producer.flush()
        print(f"Successfully sent image and label {label} to Kafka.")
    
    except Exception as e:
        print(f"Error sending image to Kafka: {e}")

try:
    for _ in range(NUM_MESSAGES):
        random_index = random.randint(0, len(images) - 1)
        image_data = images[random_index]
        image_label = label_names[labels[random_index]]
        send_image_to_kafka(image_data, image_label)
        time.sleep(0.2)
except Exception as e:
    print(f"Error sending images: {e}")
finally:
    producer.close()
    print("Kafka producer closed.")

# Wait for all messages to be processed by the consumer
all_messages_received.wait()

print(f"Latency data saved to {latency_file_path}")