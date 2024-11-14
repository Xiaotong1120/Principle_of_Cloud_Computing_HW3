import os
import json
from kafka import KafkaConsumer
import couchdb
import threading

# Connect to CouchDB server and create/select the database
try:
    # Connect to CouchDB using the provided credentials and URL
    couch = couchdb.Server('http://admin:admin@192.168.5.51:30084/')
    
    # Check if the 'img_db' database exists, if not, create it
    if 'img_db' not in couch:
        db = couch.create('img_db')
    else:
        db = couch['img_db']
    print("Connected to CouchDB successfully.")
except Exception as e:
    # Handle CouchDB connection error
    print(f"Failed to connect to CouchDB: {e}")

# Initialize Kafka consumer to read image data from 'iot-topic'
try:
    consumer_iot = KafkaConsumer(
        'iot-topic',
        bootstrap_servers=["192.168.5.142:30092"],  # Kafka broker address
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),  # Deserialize JSON data from messages
        auto_offset_reset='earliest',  # Start reading from the earliest available message
        enable_auto_commit=True,  # Automatically commit the message offsets
        group_id='iot-consumer-group'  # Consumer group ID for managing multiple consumers
    )
    print("Kafka consumer for 'iot-topic' initialized successfully.")
except Exception as e:
    # Handle Kafka consumer initialization error for 'iot-topic'
    print(f"Failed to initialize Kafka consumer for 'iot-topic': {e}")

# Initialize Kafka consumer to read inference predictions from 'iot-predictions'
try:
    consumer_predictions = KafkaConsumer(
        'iot-predictions',
        bootstrap_servers=["192.168.5.142:30092"],  # Kafka broker address
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),  # Deserialize JSON data from messages
        auto_offset_reset='earliest',  # Start reading from the earliest available message
        enable_auto_commit=True,  # Automatically commit the message offsets
        group_id='iot-predictions-group'  # Consumer group ID for managing multiple consumers
    )
    print("Kafka consumer for 'iot-predictions' initialized successfully.")
except Exception as e:
    # Handle Kafka consumer initialization error for 'iot-predictions'
    print(f"Failed to initialize Kafka consumer for 'iot-predictions': {e}")

# Function to store image data into CouchDB
def store_image_data_in_db(data):
    try:
        # Prepare the document to store in CouchDB, including the image data, ground truth, and producer ID
        doc = {
            "_id": data['ID'],  # Use the image ID as the document ID in CouchDB
            "GroundTruth": data['GroundTruth'],  # Store the ground truth label
            "Data": data['Data'],  # Store the image data
            "producer_id": data['producer_id']  # Store the producer ID for tracking
        }
        # Save the document to CouchDB
        db.save(doc)
        print(f"Stored image data with ID: {data['ID']}")
    except Exception as e:
        # Handle error in saving image data to CouchDB
        print(f"Error saving image data to CouchDB: {e}")

# Function to update prediction results in CouchDB
def update_prediction_in_db(data):
    try:
        image_id = data['ID']  # Get the image ID for the document to update
        inferred_value = data['InferredValue']  # Get the inferred class label

        # Check if the document with the given ID exists in the database
        if image_id in db:
            doc = db[image_id]  # Retrieve the document by ID
            doc['InferredValue'] = inferred_value  # Update the document with the inferred value
            db.save(doc)  # Save the updated document back to CouchDB
            print(f"Updated InferredValue for image ID: {image_id}")
        else:
            # Handle case where the document does not exist in CouchDB
            print(f"Document with ID {image_id} not found in CouchDB.")
    except Exception as e:
        # Handle error in updating prediction data in CouchDB
        print(f"Error updating prediction in CouchDB: {e}")

# Thread 1: Consume image data from 'iot-topic' and store it in CouchDB
def consume_iot_topic():
    try:
        for message in consumer_iot:
            image_data = message.value  # Extract the image data from the message
            print(f"Received image data from Kafka: {image_data}")
            store_image_data_in_db(image_data)  # Store the image data in CouchDB
    except Exception as e:
        # Handle any error that occurs during message consumption
        print(f"Error consuming image data from 'iot-topic': {e}")
    finally:
        # Ensure the Kafka consumer is closed gracefully
        consumer_iot.close()

# Thread 2: Consume prediction results from 'iot-predictions' and update CouchDB
def consume_predictions_topic():
    try:
        for message in consumer_predictions:
            prediction_data = message.value  # Extract the prediction data from the message
            print(f"Received prediction result from Kafka: {prediction_data}")
            update_prediction_in_db(prediction_data)  # Update CouchDB with the prediction result
    except Exception as e:
        # Handle any error that occurs during message consumption
        print(f"Error consuming prediction data from 'iot-predictions': {e}")
    finally:
        # Ensure the Kafka consumer is closed gracefully
        consumer_predictions.close()

# Start two separate threads for consuming image data and prediction results
thread_iot = threading.Thread(target=consume_iot_topic)
thread_predictions = threading.Thread(target=consume_predictions_topic)

thread_iot.start()  # Start the image data consumption thread
thread_predictions.start()  # Start the prediction results consumption thread

# Wait for both threads to complete before exiting
thread_iot.join()
thread_predictions.join()

print("Kafka consumers closed.")