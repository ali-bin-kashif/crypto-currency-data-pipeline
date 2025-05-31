# Crypto Data Pipeline — AWS Glue, Lambda, S3, Snowflake, Airflow
A scalable crypto data pipeline that ingests from API, transforms, stores, and loads crypto currencies historical and intra day data using AWS services and Snowflake. Airflow orchestrates the entire pipeline and, CI/CD fully automated through GitHub Actions.

## Architecture Diagram
<img src="assets/architecture_diagram.jpeg" alt="Architecture Diagram"/>


## 📚 Project Overview

| Component          | Tool / Service                |
|--------------------|-------------------------------|
| Data Ingestion     | AWS Lambda                    |
| Data Transformation| AWS Glue (PySpark)            |
| Storage            | AWS S3                        |
| Data Warehouse     | Snowflake                     |
| Orchestration      | Apache Airflow                |
| CI/CD              | GitHub Actions                |
| Region Alignment   | eu-north-1 (Stockholm)        |
