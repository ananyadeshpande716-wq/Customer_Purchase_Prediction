# Customer Purchase Prediction System

An academic mini-project that combines machine learning with a MongoDB-backed customer management application. The ML workflow is developed in Google Colab; the local Python application provides customer CRUD operations, purchase predictions from saved customer-history features, and prediction-history retrieval.

## Project objectives

- Explore and preprocess retail transaction data.
- Engineer customer-level features from a 90-day historical window.
- Predict whether an eligible customer will make a purchase in the following 30-day window.
- Compare classification models using chronological validation and held-out test data.
- Store customer profiles and prediction history in MongoDB Atlas.
- Provide a Streamlit interface for customer management and predictions.

## Technology stack

- Python 3.12 for the local application environment
- Google Colab for AIML experimentation
- pandas and NumPy for data preparation
- scikit-learn 1.6.1 for model training and inference compatibility
- joblib for model persistence
- MongoDB Atlas and PyMongo for NoSQL data storage
- Streamlit for the web interface
- python-dotenv for local environment configuration

## Repository structure

```text
Customer_Purchase_Prediction/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── notebooks/
│   └── customer_purchase_prediction.ipynb
├── models/
│   └── purchase_prediction_model.joblib
├── src/
│   ├── __init__.py
│   ├── mongodb.py
│   ├── customer_service.py
│   ├── feature_service.py
│   ├── predictor.py
│   └── prediction_service.py
├── app/
│   └── streamlit_app.py
└── tests/
    ├── test_customer_service.py
    ├── test_feature_service.py
    ├── test_prediction_service.py
    ├── test_prediction_by_customer_id.py
    └── test_prediction_readiness.py
```

Some folders may contain additional files as development continues. The raw dataset and local secrets should not be committed to GitHub.

## Dataset

The project uses the **UCI Online Retail** dataset, containing transaction records from a UK-based online retailer between December 2010 and December 2011.

Dataset source: https://archive.ics.uci.edu/dataset/352/online-retail

Download `Online Retail.xlsx` and place it in Google Drive at the location expected by the notebook:

```text
MyDrive/customer-purchase-prediction/data/raw/Online Retail.xlsx
```

The notebook starts with the original Excel data and performs preprocessing and feature engineering itself. It does not require a pre-cleaned transaction file as input. The original data should remain unchanged; cleaned transactions and customer-level modeling data are derived outputs.

## Machine-learning workflow

The single Colab notebook includes:

1. Library imports and dataset loading
2. Dataset inspection and exploratory data analysis
3. Data cleaning and preprocessing
4. Customer-level feature engineering using the preceding 90 days
5. Target creation for purchases in the following 30 days
6. Chronological/rolling validation and model comparison
7. Decision-threshold selection using validation data
8. Held-out test evaluation and visualizations
9. Saving the selected model artifact and reports

The current saved model is **Histogram Gradient Boosting**, version `purchase-model-20261022T221804Z`, with a decision threshold of `0.425`. Its input features are:

- `recency_days`
- `orders_last_90d`
- `spend_last_90d`
- `quantity_last_90d`
- `unique_products_last_90d`
- `avg_order_value_90d`

### Reported held-out test results

These are the results reported by the current notebook run; rerunning the experiment may produce different results if the data or code changes.

| Metric | Histogram Gradient Boosting |
|---|---:|
| Accuracy | 0.6119 |
| Precision | 0.5048 |
| Recall | 0.6918 |
| F1-score | 0.5837 |
| ROC-AUC | 0.6865 |
| Average precision | 0.6263 |

The majority-class baseline achieved 0.6067 accuracy on the same held-out set. The modest accuracy improvement should be discussed alongside the model's recall, F1-score, and ranking metrics rather than presented as a large improvement.

## Important scope and limitation

The dataset covers **2010–2011**. A prediction for a stored historical snapshot estimates the purchase outcome in the 30-day window following that historical snapshot. It is not a validated forecast of a customer's real-world purchasing behaviour in 2026. The website retrieves the latest feature snapshot available in MongoDB; if that snapshot is historical, the result remains a historical demonstration. Using the system for current business decisions would require recent transaction data and validation on a more recent time period.

A customer profile in the `customers` collection does not automatically create purchase history. A prediction is possible only when a usable feature snapshot exists in `customer_features`.

## MongoDB collections

The application uses MongoDB Atlas. The main collections are:

- `customers`: customer profiles managed by the CRUD interface.
- `customer_features`: customer-level historical features used as model inputs.
- `prediction_history`: generated predictions, probabilities, thresholds, feature snapshot dates, and model metadata.

The application can create customer profiles, search/filter/paginate records, update and delete profiles, generate predictions for customers with available feature snapshots, and retrieve prediction history.

## Local setup

### 1. Clone the repository

```powershell
git clone https://github.com/ananyadeshpande716-wq/Customer_Purchase_Prediction.git
cd Customer_Purchase_Prediction
```

### 2. Create and activate a Python 3.12 virtual environment

Python 3.12 is used locally to match the model's scikit-learn version.

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The trained model was serialized with scikit-learn 1.6.1. Keep that version aligned with the version specified in `requirements.txt` when loading the saved `joblib` artifact.

### 4. Configure MongoDB Atlas credentials

Copy `.env.example` to `.env` and set your own connection details:

```dotenv
MONGODB_URI=mongodb+srv://<database-user>:<encoded-password>@<cluster-host>/?retryWrites=true&w=majority
MONGODB_DATABASE=customer_purchase_prediction
```

Replace the placeholders with your own Atlas values. Configure Atlas Database Access and Network Access so your computer is allowed to connect. Do not commit `.env`, paste credentials into source code, or share your connection string.

Before using prediction features, ensure `customer_features` contains feature snapshots generated from the notebook/data workflow. The Streamlit application does not create historical features merely by registering a customer profile.

### 5. Run the application

From the repository root, with the virtual environment active:

```powershell
python -m streamlit run app/streamlit_app.py
```

Open the local address printed by Streamlit, usually `http://localhost:8501`.

## Running tests

Tests are integration tests that connect to MongoDB Atlas. Ensure `.env` is configured and the Atlas cluster is reachable before running them.

```powershell
python -m tests.test_customer_service
python -m tests.test_feature_service
python -m tests.test_prediction_service
python -m tests.test_prediction_by_customer_id
python -m tests.test_prediction_readiness
```

The tests create temporary customer or prediction records and attempt to remove those records afterward. Run them against a development database, not a production database.

## Security and data hygiene

- Never commit `.env`, MongoDB credentials, or virtual-environment folders.
- Keep the raw Excel dataset out of GitHub unless its inclusion is necessary and permitted.
- Load the included model artifact only from a trusted source.
- The application is an academic prototype, not a production-hardened customer data system.

## Future improvements

- Import more recent transaction data and re-evaluate the model temporally.
- Add pagination and indexes appropriate to the actual MongoDB query patterns.
- Add automated tests that can run against a disposable test database.
- Add deployment configuration and user authentication if the application is hosted for other users.

## Author and academic use

This repository was developed as a combined AIML and Advanced Database Management Systems mini-project. Update this section with your course details, team members, and submission information before final submission.
