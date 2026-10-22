# Customer Purchase Prediction Using Machine Learning and MongoDB

A mini-project that predicts whether a customer is likely to make at least one valid purchase in the next 30 days, using historical transaction behaviour. MongoDB will store customer features and prediction history.

## Project status

- [ ] Dataset understanding and exploratory data analysis
- [ ] Transaction data cleaning
- [ ] Customer feature engineering and 30-day target creation
- [ ] Model training and chronological evaluation
- [ ] MongoDB integration
- [ ] Streamlit dashboard
- [ ] Testing and final report

## Dataset

We plan to use the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online-retail). Download the dataset separately and place the source file under `data/raw/` for local execution, or access it from Google Drive in Google Colab.

**Do not commit the raw dataset, credentials, `.env` files, or private customer data to GitHub.** See `data/README.md`.

## Planned technology stack

- Python, Pandas, NumPy, Matplotlib / Seaborn, scikit-learn
- Google Colab for development and model experiments
- MongoDB Atlas with PyMongo
- Streamlit for a simple dashboard
- Git and GitHub for version control

## Planned repository structure

```text
customer-purchase-prediction/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── data/
│   ├── README.md
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_preprocessing_features.ipynb
│   └── 03_model_training_evaluation.ipynb
├── src/
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── predict.py
│   └── mongodb.py
├── app/
│   └── streamlit_app.py
├── models/
├── reports/
│   ├── results.md
│   └── figures/
└── tests/
    └── test_preprocessing.py
```

Files will be added as we implement each phase; this structure is a plan, not a claim that every component is implemented yet.

## Target definition (planned)

For a customer snapshot date, build features from the previous 90 days and label the customer as `1` if they make at least one valid purchase in the following 30 days, otherwise `0`. Only snapshots with a fully observed 30-day prediction window will be used. We will split snapshots chronologically to reduce temporal leakage.

## Running the project

Instructions will be added as implementation is completed. Initial data exploration and model development will be done in Google Colab.
