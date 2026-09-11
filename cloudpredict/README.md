# CloudPredict

CloudPredict is a cross-platform serverless performance and cost predictor for AWS, Azure, and Google Cloud Platform (GCP).

## Installation

You can install CloudPredict directly using pip from the built wheel, or from source:

```bash
pip install .
```

> **Note**: CloudPredict requires `scikit-learn==1.5.0` to load the pre-trained models safely.

## Usage

CloudPredict offers two main commands: `predict` and `analyze`.

### 1. Manual Prediction

Manually predict performance and cost for a specific configuration:

```bash
cloudpredict predict --platform aws --runtime python --region us-east-1 --input-size 1024 --workload cpu_math_2_xs_v1
```

### 2. Project Analysis

Analyze a local script or project directory and get recommendations for the best cloud platform based on inferred runtime and workload:

```bash
cloudpredict analyze ./my-serverless-project
```

## Limitations

- **Workload Classification**: The project analysis uses a keyword-heuristic approach to classify workloads, not a trained classifier. It infers workload type based on imports and common keywords.
- **Predictions Bounded by Training Data**: The ML predictions are constrained by the original benchmark categories and regions used during training.
