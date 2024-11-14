# IoT Data Analytics Pipeline Using Kafka, Docker, and Kubernetes

## Project Overview

This project builds a distributed IoT data analytics pipeline using **Kafka**, **Docker**, and **Kubernetes**, processing the CIFAR-10 dataset. With Kubernetes managing containerized services, the system achieves data generation, machine learning inference, and result storage. Automated deployment is handled via Ansible Playbooks, enabling a scalable real-time data processing system.

---

## System Architecture

### Key Components

1. **Producers**  
   - Load images from the CIFAR-10 dataset and send them to Kafka topics.  
   - Compute end-to-end latency by recording the time from sending images to receiving inference results.

2. **Inference Service**  
   - Receive images from Kafka topics, perform inference using a ResNet model, and send the predicted labels back to Kafka.

3. **Consumers**  
   - Retrieve inference results from Kafka topics and store them in a CouchDB database.

4. **CouchDB**  
   - A reliable NoSQL database for storing inference results and raw image data.

---

### Pod Architecture

All services are deployed as Pods in a Kubernetes cluster, managed dynamically:

- **Kafka and Zookeeper Pods**: Ensure smooth communication between Producers, Inference Services, and Consumers.  
- **Producer Pods**: Generate and send image data, calculate latency, and scale to multiple instances for load testing.  
- **Inference Pods**: Perform inference on image data using the ResNet model and return the results to Kafka.  
- **Consumer Pods**: Retrieve inference results and store them in CouchDB.  
- **CouchDB Pod**: Provides persistent database services for inference results and original images.

---

## Key Features

- **Scalability**  
  Producer Pods can dynamically scale up to five instances to simulate different workloads.

- **Automated Deployment**  
  Kubernetes clusters and services are deployed via Ansible Playbooks, ensuring reproducibility.

- **Latency Analysis**  
  Producers log the time from sending images to receiving inference results, generating latency data files for analysis.

- **Database Storage**  
  Consumers persist results and raw images in CouchDB for further processing.

---

## Technology Stack

- **Kubernetes**: Automates distributed service management and scaling.
- **Kafka**: Provides high-throughput message transmission between services.
- **PyTorch**: Implements image classification using a pre-trained ResNet model.
- **CouchDB**: A NoSQL database for efficient data storage.
- **Ansible**: Automates the deployment and configuration of virtual machines and services.

### Python Dependencies
- `kafka-python`: Implements Kafka producers and consumers.
- `torch` and `torchvision`: Enable machine learning inference and provide pre-trained models.
- `Pillow`: Handles image conversion and encoding.
- `couchdb`: Connects to the CouchDB database.
- `numpy`: Assists with data analysis and numerical computations.

---

## Workflow

1. **Cluster Initialization and Service Deployment**
   - Ansible Playbooks initialize Kubernetes clusters and deploy services, including Kafka, Zookeeper, Producers, Inference Services, and Consumers.
   - Kubernetes manages Pod scheduling and service scaling.

2. **Data Generation and Inference**
   - Producers load CIFAR-10 images and send them to Kafka topics.
   - Inference services use the ResNet model to classify images and send the results back to Kafka.

3. **Result Storage and Analysis**
   - Consumers retrieve inference results from Kafka and store them in CouchDB.
   - Producers log latency data and generate files for percentile calculations.

4. **Latency Analysis and Load Testing**
   - Test system performance under various producer counts and calculate the 90th and 95th percentiles for latency data.

---

## Team Contribution

The project was developed collaboratively, with team members taking on different roles to ensure smooth progress:

- **Ansible Playbook Development**  
  - **Xiaotong 'Brandon' Ma**, **Sparsh Amarnani**  
  - Developed playbooks for initializing Kubernetes clusters and installing Kafka, Zookeeper, Docker, and other services.

- **Basic Kubernetes Setup and Testing**  
  - **Xiaotong 'Brandon' Ma, Arpit Ojha**  
  - Validated basic Kubernetes cluster functionality, ensuring Pods were deployable and services were running.

- **Advanced Kubernetes Configuration and Troubleshooting**  
  - **Xiaotong 'Brandon' Ma**  
  - Configured advanced Kubernetes settings, solved inter-Pod communication issues, enabled HostNetwork, and adjusted DNS settings for seamless connectivity.

- **All Other Development and Integration**  
  - **Xiaotong 'Brandon' Ma**  
  - Developed the Producer, Inference, and Consumer scripts; built Docker images; integrated all components; conducted performance testing; and wrote final documentation.

Team communication was facilitated through Slack to ensure timely collaboration and coordination.

---

## Results and Achievements

- **Distributed Data Pipeline**  
  Successfully implemented a distributed IoT data analytics pipeline, completing the full cycle from data generation to inference and storage.

- **Performance Metrics**  
  Generated latency data files and analyzed the system performance under various workloads, computing 90th and 95th percentiles.

- **Automation and Scalability**  
  The system is highly automated and can dynamically scale, meeting diverse performance testing requirements.

---
