# Running a Dockerized model on a Google kubernetes cluster

This repository explains:

* How to install Docker, specifically on a Windows machine;
* How to build and deploy a hello-world app on local host and GCP (Google Cloud Platform);
* How to build and run a model (for POC) in a container and serve it on local host and deploy it in a scalable Kubernetes Cluster on GCP.

For those who need a bit more introduction on Docker, these items are preceded by an Introduction. We want to highlight it is not necessary to go through all the steps. For instance, if you already have Docker running on your machine and know how to interact with GCP you may want to jump straight to chapter 4.


## 1. Introduction on Docker

Online you can find many introductions and tutorials on Docker. For this brief introduction mainly take from: 

https://towardsdatascience.com/how-docker-can-help-you-become-a-more-effective-data-scientist-7fc048ef91d5


#### 1.1. What is Docker?
You can think of Docker as lightweight virtual machines that contain everything you need to run an application. A docker container can capture a snapshot of the state of your system so that someone else can quickly re-create your compute environment.

#### 1.2. Why should you use docker (in combination with Kubernetes)?
* Reproducibility: 
It is really important that your work is reproducible as a professional data scientist. Reproducibility not only facilitates peer review, but ensures the model, application or analysis you build can run without friction which makes your deliverables more robust and withstand the test of time. For example, if you built a model in python it is often not enough to just run just pip-freeze and send the resulting requirements.txt file to your colleague as that will only encapsulate python specific dependencies — whereas there are often dependencies that live outside python such as operating systems, compilers, drivers, configuration files or other data that are required for your code to run successfully. Even if you can get away with just sharing python dependencies, wrapping everything in a Docker container reduces the burden on others of recreating your environment and makes your work more accessible.
* Portability of your compute environment:
As a data scientist, especially in machine learning, being able to rapidly change your compute environment can drastically effect your productivity. Data science work often begins with prototyping, exploring and research — work that doesn’t necessarily require specialized computing resources right off the bat. This work often occurs on a laptop or personal computer. However, there often comes a moment where different compute resources would drastically speed up your workflow —for example a machine with more CPUs or a more powerful GPU for things like deep learning. I see many data scientists limit themselves to their local compute environment because of a perceived friction of re-creating their local environment on a remote machine. Docker makes the process of porting your environment (all of your libraries, files, etc.) very easy (check next bullet point). Lastly, creating a docker file allows you to port many of the things that you love about your local environment — such as bash aliases or vim plugins.
* Strengthen your engineering chops:
A common method for deploying Machine Learning (ML) models into production, is to expose them as RESTful API hosted from within Docker containers, subsequently deployed in a cloud environment which enables everything required for maintaining continuous availability, e.g. fail-over, auto-scaling, load balancing and rolling service updates. Though, the configuration details for a continuously available cloud deployment are specific to the used cloud provider. For instance the process for AWS (Amazon Web Services) is not the same as that of GCP or Microsoft Azure. Then Kubernetes comes in handy. Kubernetes provides a single mechanism for defining entire microservice-based application deployment topologies and their service-level requirements for continuous availability. It is independent of the used cloud provider, can be run on-premise and even on a local machine.

#### 1.3. Docker Terminology
Before we dive in, it's helpful to be familiar with Docker terminology:

* Image: 
Is a blueprint for what you want to build. Ex: Ubuntu + TensorFlow with Nvidia Drivers and a running Jupyter Server.
Container: Is an instantiation of an image that you have brought to life. You can have multiple copies of the same image running. It is really important to grasp the difference between an image and a container as this is a common source of confusion for new comers. If the difference between an image and a container isn’t clear, STOP and read again.
* Dockerfile:
Recipe for creating an Image. Dockerfiles contain special Docker syntax. From the official documentation: A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image.
* Commit: 
Like git, Docker containers offer version control. You can save the state of the docker by committing the changes.
* DockerHub / Image Registry: 
Place where people can post public (or private) docker images to facilitate collaboration and sharing.
* Layer: 
modification to an existing image, represented by an instruction in the Dockerfile. Layers are applied in sequence to the base image to create the final image.

An example of a Docker file:
A Dockerfile has INSTRUCTIONS and arguments. It is not necessary that they be capitalized, but it is the convention. Some of these instructions we will use later on in our example:

* FROM: 
The FROM statement specifies the base image. In our example, we are taking the postgres base image from Dockerhub.

* LABEL: 
The LABEL statement adds metadata to your image, and is completely optional. I add this such that others know who to contact about the image and also so I can search for my docker containers, especially when there are many of them running concurrently on a server.

* RUN: 
The RUN statement is the workhorse of the Dockerfile. In our case, we are using it to run shell commands. These commands have nothing to do with Docker but are basic Linux commands.

* WORKDIR:
The WORKDIR statement is often sued to specify a working directory. Any subsequent commands will assume that is the working directory.

* ADD:
The ADD statement lets you copy files from the host machine to the docker container.

* CMD:
The CMD statement is used to provide defaults when executing a container. Only one CMD statement is valid per container, and if you provide several, only the last one will be used by the container.

More information on Docker commands can be found here: https://docs.docker.com/engine/reference/builder/

## 2. Installation of Docker on a Windows machine

#### 2.1. Requirements
As explained on:

https://docs.docker.com/docker-for-windows/install/

Docker for windows requires amongst others that you run Windows 10 64bit: Pro, Enterprise or Education. That's because Docker Desktop for Windows requires Microsoft Hyper-V to run. Previously there was a work around for Windows home edition, via the use of toolbox (https://docs.docker.com/toolbox/overview/), but this no longer works correctly. Although it is possible to run Docker itself (build images and run containers), you will run into problems when testing, e.g. with port exposure, something we will do in this exercise.

If you have Windows Home edition, it is best to first upgrade to a pro version, e.g. via 'Start > Windows Update' (price approx. $150).

#### 2.2. Installation instructions
Create a Docker account as explained on:

https://docs.docker.com/docker-id/

Then download Docker for Windows via:

https://hub.docker.com/editions/community/docker-ce-desktop-windows

Double-click Docker for Windows Installer to run the installer.

Open a command-line terminal and try some Docker commands:

Run:
```
docker version 
```
to check the version.

Run:
```
docker run hello-world 
```
to verify that Docker can pull and run images.


## 3. How to build and deploy a hello-world app on local host and GCP (Google Cloud Platform)

#### 3.1. Introduction / prerequisites
Before we are going to deploy a model, we are first going to test a simple hello-world web server application and deploy it on GCP in a Kubernetes cluster.

You can use the GCP account of the company. Otherwise you will need to sign-up for an account and create a project. Check the various sources on the internet to see how to do this. 

Make sure that the GCP SDK is installed on your local machine. We then need to initialize the SDK via the command:
```
gcloud init
```
This will open a browser and will guide you through the necessary authentication steps. Make sure you pick the project you created, together with a default zone and region. 

If you already have default settings, you can check those via:
```
gcloud info
```

#### 3.2. Instructions

After cloning this repository to your local machine, cd into the hello-world folder of the repository. The hello-app is a simple web server application consisting of two files: main.go and a Dockerfile. Please feel free to open the Docker file to check the Docker instructions. To build the image from this Docker file and tag it with 'hello-app:v1', run the following command in cmd (don't forget the closing dot!):

```
docker build -t hello-app:v1 .
```

To test your container image using your local Docker engine, run the following command:
```
docker run --rm -p 8080:8080 hello-app:v1
```
You can then check whether the app is working correctly via 'http://localhost:8080', or via (another) command prompt:
```

curl http://localhost:8080

```

To stop the container, find its ID in the container list:
```
docker ps
```

and the stop the container with this ID, for instance:
```
docker stop 7852490686e8 
```

Before we can host our app through GCP, we upload the image to docker repository. Note: We do not use the GCP Image repository, because this gives problem when Kubernetes wants to pull the image. We do not have these problems when pulling from the Docker repository, even when you set the repository to 'private'. In that case you can first create a private repository in docker hub and push the image to that repository. With the free account of Docker you are only allowed to have one private repository and we believe unlimited number of public ones. Thus we advise to use the private one for launches to cloud platforms like GCP.

first check for the id with:
```
docker images
```
then prior to uploading it to Docker, tag the image with your docker accountname and label:
```
docker tag 2bdafa5679e8 robertvanoverbeek/hello-world:v1
```
It could be the case that you need to login to Docker, this can be done with:
```
docker login
```
Otherwise, push the image to Docker hub with:
```
docker push robertvanoverbeek/hello-world:v1
```

We then create a kubernetes cluster on GCP with (in this case with 2 nodes and the name hello-cluster):
```
gcloud container clusters create hello-cluster --num-nodes=2
```

When the cluster is created, we can run the container, using the Docker repository. So you should replace the image name with your repository. We deploy your application, listening on port 8080:
```
kubectl run hello-web --image=robertvanoverbeek/hello-world:v1 --port 8080
```
To see the Pod created by the Deployment and check it is running, run the following command:
```
kubectl get pods
```

We then expose the application to the Internet. By default, the containers you run on GKE are not accessible from the Internet, because they do not have external IP addresses. Check this via:
```
kubectl get service
```

You must explicitly expose your application to traffic from the Internet, run the following command:
```
kubectl expose deployment hello-web --type=LoadBalancer --port 80 --target-port 8080
```
Then check the service again via.
```
kubectl get service
```
With the previous command you can also retrieve the external ip address and check that the app is working correctly. In our case we had ip 35.241.237.159, so we used the browser, or used curl:

```
curl http://35.241.237.159
```

This should result in something like this:

Hello, world!
Version: 1.0.0

You can delete the deployment with:
```
kubectl delete deployment hello-web
```
In order to avoid costs, in case you will not use the cluster in the very near future, delete the cluster with:
```
gcloud container clusters delete hello-cluster
```
When asked, confirm with 'Y'.

#### 3.2. Note on cleaning up containers and images

In case you want to keep a clean sheet of containers and images, we provide you with two commands to clean up:
```
docker system prune
```
You can then check that the clean-up was successful:
```
docker ps -a
```

```
docker image prune -a
```
You can then check that the clean-up was successful:
```
docker images
```

## 4. How to build and run a simple linear sklearn model (for POC) in a container and serve it on local host and then deploy it in a scalable Kubernetes Cluster on GCP.

#### 4.1. Introduction

This repository contains a directory 'model', which contains everything we need to deploy a simple linear model (using sklearn) in a container and to make online predictions via localhost and (optionally) GCP. We will be using Flask to publish our model. Flask is a micro web framework written in Python. Coming to Flask, it is a web service development framework in Python. A Web service is a form of API which assumes that an API is hosted over a server and can be consumed. Web API, Web Service - these terms are generally used interchangeably. Why use an API in Data Science in Predictive modeling? Generally the application of a machine learning model sits at the heart of an end product, for instance a small component of a recommender system or an intelligent chat-bot. This brings in complications. The majority of the ML practitioners use R/Python for their experiments. But consumers of those ML models would be software engineers who use a completely different technology stack, creating a mismatch. This might be solved in two ways: 

* Rewrite the code in another language, which will be very time consuming and potentially difficult, as the majority of languages like JavaScript, do not have great libraries to perform ML;
* Using a web API to bridge the gap between applications, which is much simpler. If a frontend developer needs to use your ML Model to create an ML powered web application, they just need to get the URL Endpoint from where the API is being served.

#### 4.2. Build a model container and test it on local host (RESTful API)
The model folder contains 5 files:
* init__.py file: Full explanation is beyond the scope of this repository, but files named __init__.py are used to mark directories on disk as Python package directories;
* requirements.txt: a simple file containing the libraries to be loaded;
* Dockerfile: A file with a similar structure as the hello world one, we already discussed. For some more detail on the structure we used here: https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/ Notably we highlight that the container made from this image will listen on port 80, so different compared with flask default port 5000. Following the instructions behind the link, we have changed this. In our case to 8080;
* main.py file: Containing the Flask structure and the model, which we discuss in more detail below;
* model_launch.yaml: File containing kubectl instructions to automatically set and activate the application on a Kubernetes cluster. Last paragraph of this chapter.

If you check the main.py file in the model directory, you will see a more or less standard Flask structure. The structure is similar to the very simple Flask structure that will just print "Hello World!":
```
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
```

Within this basic structure we build and apply the model. We load the standard diabetes dataset from sklearn, of which we use just one feature for simplicity here. We then fit a simple linear model (we do not apply training and testing here) and then save the model with pickle dump. Python pickle module is used for serializing and de-serializing a Python object structure. Any object in Python can be pickled so that it can be saved on disk. Pickling is a way to convert a python object (list, dict, etc.) into a character stream with the idea that this character stream contains all the information necessary to reconstruct the object later on. We use two routes namely '/isAlive', to test if the service is live and '/prediction' to post features and get a prediction in return.

In order to test it, cd into the model folder of this git repository. Then we can build the image right away with (note: tag it with your Docker username, followed by a name):

```
docker build --tag robertvanoverbeek/diabetes:v1 .
```

We are then going to run and test it locally. Here we start the container in detach mode, -d. You can also use --detach.
You may want to use this if you want a container to run but do not want to view and follow all its output.

```
docker run --name test-api -p 9000:8080 -d robertvanoverbeek/diabetes:v1
```

Where we have mapped port 8080 from the Docker container - i.e. the port our ML model-scoring service is listening to - to port 9000 on our host machine (localhost). As a reminder, note that we can check that the container is running with the command:
```
docker ps
```
Then:
```
curl http://localhost:9000/isAlive
```

should return 'true'

And:
```
curl http://localhost:9000/prediction/?f=0.05
```
should return a prediction. Something like 199.6.

If everything works correctly, we can then stop the container and remove it with:
```
docker stop test-api
```
```
docker rm test-api
```

#### 4.3. Deploy the model on GCP in a scalable Kubernetes Cluster

Following the local test discussed in the previous paragraph we are ready to push the image to Docker hub:
```
docker push robertvanoverbeek/diabetes:v1
```
While the image is being pushed to Docker hub, we start up a kubernetes cluster:

```
gcloud container clusters create model-test-cluster --num-nodes 3 --machine-type g1-small
```
Note, if you want to delete this cluster at a later stage, use:
```
gcloud container clusters delete model-test-cluster
```

We run the application with:
```
kubectl run diabetes-api --image=robertvanoverbeek/diabetes:v1 --port=8080 --generator=run/v1
```

We check the pods with:
```
kubectl get pods
```
You should first get the message container creating:
```
NAME                 READY     STATUS              RESTARTS   AGE
diabetes-api-nwz8z   0/1       ContainerCreating   0          58s
```
Followed by status 'RUNNING'.

Though, this does not yet mean that the service is exposed to the outside world. You can see this if you run:
```
kubectl get services
```
Which should return something like this, without an external IP address:
```
NAME         TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.55.240.1   <none>        443/TCP   14m
```

We expose the deployement with:

```
kubectl expose replicationcontroller diabetes-api --type=LoadBalancer --name diabetes-api-http
```
Note, the name is the service name, which we will use later on to delete it.

We then want to retrieve the external IP address of the app with:
```
kubectl get services
```
This should return something which looks like:
```
NAME                TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
diabetes-api-http   LoadBalancer   10.35.253.27   35.205.66.4   8080:30536/TCP   55s
kubernetes          ClusterIP      10.35.240.1    <none>        443/TCP          4m
```
Once we have the EXTERNAL-IP we are ready to test our service on GCP. First with our 'isAlive' test, which should return 'true'. In the browser, or via curl:
```
curl http://35.205.66.4:8080/isAlive
```
Then we are ready for a prediction:
```
curl http://35.205.66.4:8080/prediction/?f=0.05
```
This should return a result of approximately 199.6.

Finally, we stop the load balancer and service with the command:
```
kubectl delete replicationcontroller diabetes-api
```
and
```
kubectl delete service diabetes-api-http
```

Note, if you run:
```
kubectl get services
```

You should still see the kubernetes cluster mentioned, something like this:
```
NAME         TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.55.240.1   <none>        443/TCP   21m
```

#### 4.4. Using a YAML file to define and deploy our service

So far we have been using Kubectl commands to define and deploy our services, which is fine for testing and small applications. Otherwise it is better to use YAML files to define services and  to post those to the Kubernetes API. The included model_launch.yaml file is an example of how our model service can be defined. Note, if you do not yet have a Kubernetes cluster running, you can launch one with:
```
gcloud container clusters create model-test-cluster --num-nodes 3 --machine-type g1-small
```

If you open the YAML file you can see that we have defined three separate Kubernetes components: a replication controller, a load-balancer service and a namespace for all of these components. We use --- to delimit each component. More information on namespaces: https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/

IMPORTANT: In the yaml file repace the current image name 'image: robertvanoverbeek/diabetes' with your Docker hub username and repository name, where you have saved the image.

Then you can execute the yaml file with a single command:
```
kubectl apply -f model_launch.yaml
```
Which should return something like this:
```
namespace "test-ml-app" created
replicationcontroller "test-ml-score-rc" created
service "test-ml-score-lb" created
```
To see all components deployed in this namespace (and to check for the external ip address) use:
```
kubectl get all --namespace test-ml-app
```
With the external ip address we can test the application, similar to:
```
curl http://35.233.16.65:8080/prediction/?f=0.05
```
To remove the application we can use the single command:
```
kubectl delete -f model_launch.yaml
```

Again, if you want to delete the cluster, use:
```
gcloud container clusters delete model-test-cluster
```
