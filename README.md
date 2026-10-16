# ATM Cash Demand Forecasting and Intelligent Replenishment Using Big Data Analytics

## 📌 Project Overview

ATM Cash Demand Forecasting and Intelligent Replenishment is a Big Data Analytics project that predicts the next day's cash withdrawal demand for multiple ATMs and recommends an appropriate amount of cash to maintain at each ATM.

The project combines **Apache Kafka, Hadoop HDFS, Python-based data processing, Machine Learning, and Streamlit** to demonstrate how transaction data can be collected, processed, stored, analyzed, and used to support ATM cash replenishment decisions.

The current implementation uses a synthetic ATM transaction dataset for educational and demonstration purposes.

## 🎯 Objectives

- Analyze ATM withdrawal transaction data.
- Demonstrate transaction streaming using Apache Kafka.
- Aggregate transaction records into daily demand for each ATM.
- Store raw and processed datasets in Hadoop HDFS.
- Forecast daily ATM cash demand using a Random Forest Regressor.
- Recommend cash replenishment amounts with a safety buffer.
- Visualize transaction analytics, forecasts, and model metrics through a dashboard.

## 🏗️ System Architecture

```text
Synthetic ATM Transaction Dataset
                |
                v
         Apache Kafka
       (Producer / Topic)
                |
                v
         Kafka Consumer
                |
                v
      Consumed Transaction CSV
                |
                v
       Python + Pandas
                |
       +--------+---------+
       |                  |
       v                  v
  Hadoop HDFS       Daily Demand
  Data Storage      Aggregation
                          |
                          v
                  Feature Engineering
                          |
                          v
                  Random Forest Model
                          |
                          v
                  Next-Day Forecast
                          |
                          v
                 Cash Recommendation
                          |
                          v
                  Streamlit Dashboard
```

**Note:** HDFS provides a storage layer, while the current forecasting script reads the locally saved Kafka-consumed CSV file. The dashboard also reads local CSV files. This is a prototype pipeline, not a fully automated real-time banking system.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming and pipeline orchestration |
| Pandas | Data cleaning, aggregation, and feature engineering |
| NumPy | Numerical operations |
| Apache Kafka | Transaction event streaming |
| Hadoop HDFS | Distributed file-system storage demonstration |
| Scikit-learn | Machine learning and model evaluation |
| Random Forest Regressor | Daily cash demand forecasting |
| Joblib | Saving the trained model |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| Docker Compose | Running Kafka and Hadoop services |
| Git and GitHub | Version control and project hosting |

## 📊 Dataset

The project uses a synthetic ATM transaction dataset containing **37,910 transaction records across 8 ATMs**.

The primary dataset is stored at:

`data/atm_transactions.csv`

### Dataset fields

| Field | Description |
|---|---|
| `atm_id` | Unique identifier of the ATM |
| `timestamp` | Date and time of the transaction |
| `withdrawal_amount` | Amount withdrawn in the transaction |

The transaction records are aggregated by ATM and date to calculate daily cash demand.

### Processed outputs

- `data/kafka_consumed_transactions.csv` — transaction records consumed from Kafka.
- `data/kafka_daily_demand.csv` — daily demand and transaction statistics for each ATM.
- `data/kafka_atm_summary.csv` — aggregated statistics for each ATM.
- `data/forecast_results.csv` — next-day cash demand predictions and recommended cash amounts.
- `data/model_metrics.csv` — model evaluation metrics.

## ⚙️ Data Processing Pipeline

### 1. Transaction Streaming with Apache Kafka

A Kafka producer publishes transaction records from the dataset to a Kafka topic. A Kafka consumer reads the events and saves the consumed records into a CSV file for downstream processing.

Key components:

- Producer: `src/streaming/producer.py`
- Consumer: `src/streaming/consumer.py`
- Kafka topic used for the full dataset: `atm-transactions-full`

### 2. Data Aggregation and Analytics

The processing script validates transaction data and groups records by ATM and date.

File: `src/streaming/process_stream.py`

It generates daily statistics such as:

- Total daily withdrawal demand.
- Number of transactions.
- Average withdrawal amount.
- Maximum withdrawal amount in the ATM summary.

The processed daily dataset contains **1,440 ATM-day records**.

### 3. HDFS Storage

Hadoop HDFS is used to demonstrate the storage of raw and processed transaction datasets.

Example HDFS directory structure:

```text
/atm/
└── data/
    ├── raw/
    │   └── atm_transactions.csv
    └── processed/
        ├── kafka_consumed_transactions.csv
        ├── kafka_daily_demand.csv
        └── kafka_atm_summary.csv
```

The files are uploaded to HDFS as a separate storage step in the current implementation.

## 🤖 Machine Learning Model

The project uses a **Random Forest Regressor** to predict daily cash withdrawal demand for each ATM.

File: `src/train_model.py`

### Feature engineering

The model uses historical demand and calendar-based features:

- Previous day's demand (`lag_1`).
- Demand from two days earlier (`lag_2`).
- Demand from seven days earlier (`lag_7`).
- Seven-day rolling average.
- Fourteen-day rolling average.
- Day of the week.
- Day of the month.
- Month.
- Weekend indicator.
- Month-end indicator.

The historical features are generated from earlier observations to help predict future demand.

### Model configuration

| Parameter | Value |
|---|---:|
| Algorithm | Random Forest Regressor |
| Number of estimators | 150 |
| Maximum depth | 12 |
| Minimum samples per leaf | 2 |
| Random state | 42 |
| Training split | 80% chronological split |
| Test split | Remaining 20% of dates |

A chronological split is used so that earlier dates are used for training and later dates are used for evaluation.

### Model evaluation

The model is evaluated using:

**Mean Absolute Error (MAE):** Measures the average absolute difference between actual and predicted demand, in rupees.

**Weighted Absolute Percentage Error (WAPE):** Measures the total absolute prediction error relative to the total actual demand.

Example evaluation results from the current synthetic dataset:

| Metric | Result |
|---|---:|
| Training records | 1,056 |
| Test records | 272 |
| MAE | ₹5,684.37 |
| WAPE | 12.96% |

These results describe the current experiment and may change when the dataset or model configuration changes. They should not be interpreted as guaranteed performance on real banking data.

The trained model is saved at:

`models/atm_forecaster.joblib`

## 💰 Intelligent Cash Replenishment

After predicting the next day's cash demand, the system calculates a recommended cash amount using a 10% safety buffer and rounds it up to the next ₹500.

**Formula:**

```text
Recommended Cash = Ceiling(
    Predicted Demand × 1.10 / 500
) × 500
```

For example, if the predicted demand is ₹80,354.01:

```text
Predicted demand = ₹80,354.01
Demand with 10% buffer = ₹88,389.41
Recommended cash = ₹88,500
```

This recommendation is intended to help demonstrate how forecasting can support cash planning. Actual replenishment decisions would also require current ATM cash balances, operational constraints, and business rules.

## 📈 Dashboard

The Streamlit dashboard presents the project's transaction analytics and forecasting outputs in a visual format.

It uses the following files:

- `data/atm_transactions.csv`
- `data/forecast_results.csv`
- `data/model_metrics.csv`

The dashboard supports the demonstration of historical transactions, forecast results, recommended cash amounts, and model evaluation metrics.

## 📁 Project Structure

```text
BDA_project/
│
├── data/
│   ├── atm_transactions.csv
│   ├── kafka_consumed_transactions.csv
│   ├── kafka_daily_demand.csv
│   ├── kafka_atm_summary.csv
│   ├── forecast_results.csv
│   └── model_metrics.csv
│
├── src/
│   ├── generate_data.py
│   ├── train_model.py
│   └── streaming/
│       ├── producer.py
│       ├── consumer.py
│       └── process_stream.py
│
├── models/
│   └── atm_forecaster.joblib
│
├── hadoop/
│   ├── namenode/
│   └── datanode/
│
├── kafka-data/
├── dashboard.py
├── docker-compose.yml
└── README.md
```

*Generated datasets, model files, and local Docker storage directories may be excluded from the GitHub repository.*

## 🚀 Installation and Execution

### Prerequisites

Install the following software:

- Python 3.11 or a compatible Python version.
- Docker Desktop with Docker Compose.
- Git.
- A terminal such as PowerShell.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ATM.git
cd ATM
```

Replace `YOUR_USERNAME` with your GitHub username and use the actual repository URL.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install pandas numpy scikit-learn joblib kafka-python streamlit plotly
```

### 4. Start Kafka and Hadoop services

Ensure Docker Desktop is running, then execute:

```bash
docker compose up -d
```

Check the service status:

```bash
docker compose ps
```

### 5. Run the Kafka pipeline

Open separate terminals with the project environment activated.

Start the consumer first:

```bash
python src/streaming/consumer.py
```

In another terminal, run the producer:

```bash
python src/streaming/producer.py
```

The producer and consumer must use the matching Kafka topic and configuration. The consumer is configured for the project's expected transaction count, so use a fresh or appropriately reset Kafka topic/consumer group when repeating the complete ingestion workflow.

### 6. Process the consumed transactions

After the consumer has finished:

```bash
python src/streaming/process_stream.py
```

This generates the daily demand dataset and ATM summary.

### 7. Train the forecasting model

```bash
python src/train_model.py
```

This trains the Random Forest model, evaluates its predictions, saves the model, and generates the next-day forecast and recommended cash amounts.

### 8. Launch the dashboard

```bash
python -m streamlit run dashboard.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser to explore the dashboard.

**Execution note:** The pipeline is a sequence of scripts rather than a single automated orchestration command. The CSV files and trained model must be generated before the dashboard can display the corresponding results. HDFS uploads are a separate step.

## 🔒 Limitations and Future Enhancements

### Current limitations

- Uses synthetic rather than real banking transaction data.
- Uses a single-node educational HDFS setup.
- Uses file-based handoffs between processing and forecasting stages.
- Does not connect to live ATM balances or banking systems.
- Does not automatically trigger physical cash replenishment.
- Does not continuously update predictions from live transactions.

### Future enhancements

- Integrate secure, anonymized real-world transaction data.
- Automate HDFS ingestion and pipeline orchestration.
- Implement scheduled or streaming-based forecast updates.
- Incorporate ATM cash balance and replenishment history.
- Compare Random Forest with other forecasting models.
- Add forecast monitoring, alerts, and model drift detection.
- Deploy the application in a cloud environment.

## 🎓 Applications

This project demonstrates how Big Data technologies and Machine Learning can be combined for:

- ATM cash demand planning.
- Data-driven replenishment recommendations.
- Transaction trend analysis.
- Historical demand monitoring.
- Forecasting-based operational decision support.

## 👨‍💻 Conclusion

The project presents an educational end-to-end workflow for ATM cash demand forecasting. It demonstrates transaction streaming with Apache Kafka, analytics using Python and Pandas, storage using Hadoop HDFS, prediction using a Random Forest Regressor, and visualization through Streamlit.

By estimating next-day cash demand and applying a configurable safety buffer, the system illustrates how data-driven forecasting can support more informed ATM cash management decisions.

---

**Project Category:** Big Data Analytics, Machine Learning, Data Engineering

**Disclaimer:** This is an academic prototype built for learning and demonstration. It is not connected to real banking infrastructure and should not be used for operational cash-management decisions without further validation.
