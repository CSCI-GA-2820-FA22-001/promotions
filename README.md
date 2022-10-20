# Accounts Service

[![Build Status](https://github.com/nyu-devops/sample-accounts/actions/workflows/ci.yml/badge.svg)](https://github.com/nyu-devops/sample-accounts/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
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

## License

