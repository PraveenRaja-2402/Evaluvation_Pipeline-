# RAG Evaluation & Invoice Extraction Evaluation Summary

## 1. RAG Evaluation Pipeline

A production RAG system should be evaluated at **both retrieval and
generation stages**.

``` text
Dataset → Ground Truth → RAG Pipeline
        ↓
 Retrieval Evaluation
        ↓
 Generation Evaluation
        ↓
 Dashboard / CI-CD Gate
```

### Retrieval Metrics

  Metric              Purpose
  ------------------- ----------------------------------------------
  Context Precision   \% of retrieved chunks that are relevant
  Context Recall      \% of relevant chunks successfully retrieved
  Context Relevance   Whether retrieved context matches the query

### Generation Metrics

  Metric               Purpose
  -------------------- ------------------------------------------
  Faithfulness         Answer is supported by retrieved context
  Answer Relevancy     Answer addresses the user's question
  Answer Correctness   Matches expected answer
  Hallucination Rate   Measures unsupported/generated facts
  Citation Accuracy    Checks cited evidence
  Groundedness         Every claim is traceable to evidence

### Frameworks

-   **RAGAS:** Context Precision, Context Recall, Faithfulness, Answer
    Relevancy
-   **DeepEval:** Hallucination, Correctness, Faithfulness, Agent/RAG
    evaluation

------------------------------------------------------------------------

## 2. Invoice Extraction Evaluation

For structured extraction, evaluate **each field independently** rather
than the entire JSON.

### Recommended Pipeline

``` text
Invoice PDF
    ↓
Ground Truth JSON
    ↓
Extracted JSON
    ↓
Field-wise Evaluation
    ↓
Metrics Dashboard
```

### Recommended Metrics by Field Type

| Field            | Type          | Metric                         |
| :--------------: | :-----------: | :----------------------------: |
| SupplierName     | Text          | Exact Match + Fuzzy Similarity |
| SupplierCode     | Text          | Exact Match                    |
| InvoiceNo        | Text          | Exact Match                    |
| InvoiceDate      | Date          | Normalized Date Match          |
| PO Number        | Text          | Exact Match                    |
| VehicleNo        | Text          | Exact Match + Fuzzy            |
| CarrierName      | Text          | Exact Match + Fuzzy            |
| DriverName       | Text          | Fuzzy Similarity               |
| DriverNo         | Phone         | Exact Match                    |
| State            | Text          | Exact Match                    |
| Pincode          | Number/String | Exact Match                    |
| Amount           | Numeric       | Relative Error + Tolerance     |
| InvoiceValue     | Currency      | Normalize → Numeric Compare    |
| Quantity         | Numeric       | Numeric Compare                |
| Rate             | Numeric       | Numeric Compare                |
| Item Description | Text          | Semantic/Fuzzy Similarity      |


### Example Evaluation Output

``` json
{
  "SupplierName": {
    "prediction": "M.M SANKHLA ELECTRICALS",
    "ground_truth": "M.M SANKHLA ELECTRICALS",
    "similarity": 1.0,
    "status": "PASS"
  }
}
```

### Dashboard Example

  Field            Score Status
  -------------- ------- ---------
  SupplierName      1.00 PASS
  InvoiceNo         1.00 PASS
  InvoiceDate       1.00 PASS
  Amount           0.999 PASS
  VehicleNo         0.95 Warning
  DriverName        0.00 Missing

Overall Extraction Accuracy: **94.6%** (illustrative)

------------------------------------------------------------------------

## 3. Production Recommendation

Maintain:

-   Benchmark Invoice PDFs
-   Human-verified Ground Truth JSON
-   Automated evaluation pipeline
-   Historical metrics dashboard

Track per-field accuracy such as:

-   SupplierName Accuracy
-   InvoiceDate Accuracy
-   Amount Accuracy
-   HSN Accuracy
-   Line Item Accuracy

Integrate evaluation into CI/CD so every model or prompt change is
validated before deployment.

------------------------------------------------------------------------

## Key Takeaways

-   Evaluate **retrieval** and **generation** separately for RAG.
-   Use **RAGAS/DeepEval** for QA-style RAG systems.
-   For invoice extraction, prefer **field-level evaluation** against
    ground truth.
-   Choose metrics based on **field type**, not a single metric for all
    fields.
-   Monitor per-field accuracy to identify weak extraction areas
    quickly.
