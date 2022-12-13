# Promotions Service
[![Build Status](https://github.com/CSCI-GA-2820-FA22-001/promotions/actions/workflows/tdd.yaml/badge.svg)](https://github.com/CSCI-GA-2820-FA22-001/promotions/actions)
[![Build Status](https://github.com/CSCI-GA-2820-FA22-001/promotions/actions/workflows/bdd.yaml/badge.svg)](https://github.com/CSCI-GA-2820-FA22-001/promotions/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA22-001/promotions/branch/master/graph/badge.svg?token=D52GSICMNV)](https://codecov.io/gh/CSCI-GA-2820-FA22-001/promotions)[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-red.svg)](https://www.python.org/)


This repository contains sample code for Customer promotions for an e-commerce web site. This shows how to create a REST API with subordinate resources.


## Information about this repo

These are the RESTful routes for `promotions`
```
Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index             GET      /

list_promotions     GET      /promotions
create_promotion   POST     /promotions
get_promotion     GET      /promotions/<promotion_id>
update_promotion   PUT      /promotions/<promotion_id>
delete_promotion   DELETE   /promotions/<promotion_id>
```

The test cases have 95% test coverage and can be run with `nosetests`


## Deployment

- Open in DevContainer 

`make login` Logs into ibmcloud (you must have your api key in your host ~/.bluemix/apikey.json to be mounted by dev container)

`kubectl get all` See everything thats running

`kubectl get svc ` See services

`ibmcloud ks workers --cluster nyu-devops`  Get public ip of Kube worker node

Runs on `WORKERNODE_PUBLIC_IP:31000`

### On first deploy:
`make build`

`kubectl apply -f deploy/postgresql.yaml` 
Deploys postgres db 

`kubectl create -f deploy/deployment.yaml`		Deploys app using our promotions image, creates deployment, replicaset and pods	

`kubectl create -f deploy/service.yaml` Make accessible through service




## License

