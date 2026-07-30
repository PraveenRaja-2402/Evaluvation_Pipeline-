# This file contains information about errors that are encountered during develpment

## First run
- All code files updated, env variables added
- Observability not implemented

### Error
- On executing, i have got the below error **DeepEval model error**, **OpenTelemetry connection to host machine error**

```error
(.venv) PS C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework> python main.py --config config.yaml
2026-07-22 12:57:13 [INFO] nexsora_eval: Starting Nexsora RAG Evaluation Pipeline...
2026-07-22 12:57:13 [INFO] nexsora_eval: Scanning directories and matching documents...
2026-07-22 12:57:13 [INFO] nexsora_eval: Found 5 document pairs to evaluate.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
Traceback (most recent call last):
  File "C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework\main.py", line 124, in <module>
    main()
  File "C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework\main.py", line 71, in main
    deepeval_engine = DeepEvalEngine(llm_model=llm) if settings.evaluation.frameworks.enable_deepeval else None
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework\evaluators\deepeval_engine.py", line 12, in __init__
    self.correctness_metric = GEval(
                              ^^^^^^
  File "C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework\.venv\Lib\site-packages\deepeval\metrics\g_eval\g_eval.py", line 73, in __init__
    self.model, self.using_native_model = initialize_model(model)
                                          ^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework\.venv\Lib\site-packages\deepeval\metrics\utils.py", line 701, in initialize_model
    raise TypeError(
TypeError: Unsupported type for model: <class 'langchain_google_genai.chat_models.ChatGoogleGenerativeAI'>. Expected None, str, DeepEvalBaseLLM, GPTModel, AzureOpenAIModel, LiteLLMModel, OllamaModel, LocalModel.
Transient error StatusCode.UNAVAILABLE encountered while exporting traces to localhost:4317, retrying in 1.13s. Error details: failed to connect to all addresses; last error: UNAVAILABLE: ipv4:127.0.0.1:4317: WSAGetOverlappedResult: Connection refused (No connection could be made because the target machine actively refused it.
 -- 10061)
Failed to export traces to localhost:4317, error code: StatusCode.UNAVAILABLE, error details: failed to connect to all addresses; last error: UNAVAILABLE: ipv4:127.0.0.1:4317: WSAGetOverlappedResult: Connection refused (No connection could be made because the target machine actively refused it.
 -- 10061)
(.venv) PS C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework> 

```

### Successful run
- After updating llmfactory file and disabling Otel, please find the logs for the first successful evaluation pipeline run

```result
(.venv) PS C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework> python main.py --config config.yaml                                                                                                           
2026-07-22 13:09:23 [INFO] nexsora_eval: Starting Nexsora RAG Evaluation Pipeline...                                
2026-07-22 13:09:23 [INFO] nexsora_eval: Scanning directories and matching documents...
2026-07-22 13:09:23 [INFO] nexsora_eval: Found 5 document pairs to evaluate.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
2026-07-22 13:09:23 [INFO] nexsora_eval: Evaluating GT: img20260103_17233112.json <==> Extracted: img20260103_17233112.json
2026-07-22 13:10:19 [INFO] nexsora_eval: Evaluating GT: img20260506_09542473.json <==> Extracted: img20260506_09542473.json
2026-07-22 13:10:32 [INFO] nexsora_eval: Evaluating GT: img20260508_12144610.json <==> Extracted: img20260508_12144610.json
2026-07-22 13:10:41 [INFO] nexsora_eval: Evaluating GT: img20260508_12195287.json <==> Extracted: img20260508_12195287.json
2026-07-22 13:11:05 [INFO] nexsora_eval: Evaluating GT: img20260508_12215625.json <==> Extracted: img20260508_12215625.json
2026-07-22 13:11:21 [INFO] nexsora_eval: Exporting evaluation results...
2026-07-22 13:11:21 [INFO] nexsora_eval: Report exported to JSON: ./exports\evaluation_report.json
2026-07-22 13:11:21 [INFO] nexsora_eval: Report exported to CSV: ./exports\evaluation_report.csv
2026-07-22 13:11:24 [INFO] nexsora_eval: Report exported to Excel: ./exports\evaluation_report.xlsx
2026-07-22 13:11:24 [INFO] nexsora_eval: Report exported to Markdown: ./exports\evaluation_report.md
2026-07-22 13:11:24 [INFO] nexsora_eval: Pipeline execution completed successfully!
```
---

## Second Run - Added graffana and prometheus
- The second run successfully ran the complete extraction pipeline
- Spun up graffana and prometheus container locally
- Added prometheus and graffana dashboard to local repo
- Don't know what to do with graffana and prometheus dashboard
- Need to visually present the evaluation scores

```result
(.venv) PS C:\Nexsoverse\Project-Auomated_Upload_Extract_Download\nexsora_eval_framework> python main.py --config config.yaml
2026-07-22 15:42:04 [INFO] nexsora_eval: Starting Nexsora RAG Evaluation Pipeline...
2026-07-22 15:42:04 [INFO] nexsora_eval: Scanning directories and matching documents...
2026-07-22 15:42:04 [INFO] nexsora_eval: Found 5 document pairs to evaluate.
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
2026-07-22 15:42:04 [INFO] nexsora_eval: Evaluating GT: img20260103_17233112.json <==> Extracted: img20260103_17233112.json
2026-07-22 15:42:56 [INFO] nexsora_eval: Evaluating GT: img20260506_09542473.json <==> Extracted: img20260506_09542473.json
2026-07-22 15:43:07 [INFO] nexsora_eval: Evaluating GT: img20260508_12144610.json <==> Extracted: img20260508_12144610.json
2026-07-22 15:43:19 [INFO] nexsora_eval: Evaluating GT: img20260508_12195287.json <==> Extracted: img20260508_12195287.json
2026-07-22 15:43:42 [INFO] nexsora_eval: Evaluating GT: img20260508_12215625.json <==> Extracted: img20260508_12215625.json
2026-07-22 15:43:52 [INFO] nexsora_eval: Exporting evaluation results...
2026-07-22 15:43:52 [INFO] nexsora_eval: Report exported to JSON: ./exports\evaluation_report.json
2026-07-22 15:43:52 [INFO] nexsora_eval: Report exported to CSV: ./exports\evaluation_report.csv
2026-07-22 15:43:53 [INFO] nexsora_eval: Report exported to Excel: ./exports\evaluation_report.xlsx
2026-07-22 15:43:53 [INFO] nexsora_eval: Report exported to Markdown: ./exports\evaluation_report.md
2026-07-22 15:43:53 [INFO] nexsora_eval: Pipeline execution completed successfully!
```

**Note: Second Run - Added graffana and prometheus<br> Commit Mesage: Added Graffana and Prometheus Dashboards<br>- Need to visually present the evaluation metrices**
---

## Thrid Run - Create more visual evaluation metrices, Resolve ragas error

- On checking the exported json report, it shows ragas is facing "Ragas Engine Error: 'GeminiDeepEvalWrapper' object has no attribute 'invoke'"
- This error need to be addressed and add some improvements to result presentations

```exported_json_error
  {
    "gt_file": "img20260506_09542473.json",
    "ext_file": "img20260506_09542473.json",
    "execution_time_seconds": 10.7335,
    "deterministic": {
      "field_precision": 0.3182,
      "field_recall": 0.3182,
      "exact_match_ratio": 0.3182,
      "average_string_similarity": 0.734,
      "field_breakdown": {
        "id": {
          "ground_truth": "bed6c8d0-d7e9-4545-bd2c-477172205d22",
          "extracted": "192c60bb-b7a7-4ca1-8da0-760a5dca4eae",
          "exact_match": false,
          "similarity_score": 0.3611
        },
        "document_name": {
          "ground_truth": "img20260506_09542473.pdf",
          "extracted": "img20260506_09542473.pdf",
          "exact_match": true,
          "similarity_score": 1.0
        },
        "timestamp": {
          "ground_truth": "2026-07-20T19:07:45.995699+00:00",
          "extracted": "2026-07-22T07:11:55.609380+00:00",
          "exact_match": false,
          "similarity_score": 0.7188
        },
        "status": {
          "ground_truth": "succeeded",
          "extracted": "succeeded",
          "exact_match": true,
          "similarity_score": 1.0
        },
        "extracted_data.POnumber": {
          "ground_truth": "P270231",
          "extracted": "P2770231",
          "exact_match": false,
          "similarity_score": 0.9333
        },
        "extracted_data.SupplierName": {
          "ground_truth": "M.M.SANKHLA ELECTRICALS-FY-2023-2024 (From 1-Apr-21",
          "extracted": "M.M SANKHLA ELECTRICALS",
          "exact_match": false,
          "similarity_score": 0.5946
        },
        "extracted_data.SupplierCode": {
          "ground_truth": "",
          "extracted": "",
          "exact_match": true,
          "similarity_score": 1.0
        },
        "extracted_data.InvoiceNo": {
          "ground_truth": "32086/26-27",
          "extracted": "3206626-27",
          "exact_match": false,
          "similarity_score": 0.8571
        },
        "extracted_data.InvoiceDate": {
          "ground_truth": "2026-04-24",
          "extracted": "2026-04-26",
          "exact_match": false,
          "similarity_score": 0.9
        },
        "extracted_data.Referencenumber": {
          "ground_truth": "20260983",
          "extracted": "8861200084",
          "exact_match": false,
          "similarity_score": 0.4444
        },
        "extracted_data.VechileNo": {
          "ground_truth": "KA02JZ2560",
          "extracted": "KA02SZ2660",
          "exact_match": false,
          "similarity_score": 0.8
        },
        "extracted_data.CarrierType": {
          "ground_truth": "",
          "extracted": "Truck",
          "exact_match": false,
          "similarity_score": 0.0
        },
        "extracted_data.CarrierName": {
          "ground_truth": "",
          "extracted": "TECHSOL ENGINEERS",
          "exact_match": false,
          "similarity_score": 0.0
        },
        "extracted_data.Drivername": {
          "ground_truth": "",
          "extracted": "",
          "exact_match": true,
          "similarity_score": 1.0
        },
        "extracted_data.DriverNo": {
          "ground_truth": "",
          "extracted": "",
          "exact_match": true,
          "similarity_score": 1.0
        },
        "extracted_data.Invoicevalue": {
          "ground_truth": "\u20b9 25,204.80",
          "extracted": "\u20b9 26,204.80",
          "exact_match": false,
          "similarity_score": 0.9091
        },
        "extracted_data.Noofpakage": {
          "ground_truth": "Roll-1",
          "extracted": "1",
          "exact_match": false,
          "similarity_score": 0.2857
        },
        "extracted_data.State": {
          "ground_truth": "Karnataka",
          "extracted": "Karnataka",
          "exact_match": true,
          "similarity_score": 1.0
        },
        "extracted_data.Pincode": {
          "ground_truth": "562123",
          "extracted": "560053",
          "exact_match": false,
          "similarity_score": 0.5
        },
        "extracted_data.Amount": {
          "ground_truth": 25204.8,
          "extracted": 26204.8,
          "exact_match": false,
          "similarity_score": 0.8571
        },
        "extracted_data.Documents": {
          "ground_truth": [],
          "extracted": [],
          "exact_match": true,
          "similarity_score": 1.0
        },
        "extracted_data.Detail": {
          "ground_truth": [
            {
              "S.no": "1",
              "Amount": "21,360.00",
              "HSN/SAC": "74091900",
              "Quantity": "24.00 MTR",
              "Basic_Rate": "890.00",
              "item_description": "25MMX3MM COPPER STRIP"
            }
          ],
          "extracted": [
            {
              "S.no": "1",
              "Amount": "21,360.00",
              "HSN/SAC": "74091900",
              "Quantity": "24.00",
              "Basic_Rate": "890.00",
              "item_description": "25MMX3MM COPPER STRIP"
            }
          ],
          "exact_match": false,
          "similarity_score": 0.9869
        }
      }
    },
    "deepeval": {
      "deepeval_correctness_score": 0.3,
      "deepeval_reasoning": "The Actual Output demonstrates strong alignment with the Expected Output in terms of schema structure and data types, and no facts, numbers, dates, or schema values are missing. However, there are numerous precise value mismatches for critical fields, including `POnumber`, `SupplierName`, `InvoiceNo`, `InvoiceDate`, `Referencenumber`, `VechileNo`, `CarrierType`, `CarrierName`, `Invoicevalue`, `Noofpakage`, `Pincode`, `Amount`, and `Detail[0].Quantity`, indicating significant inaccuracies in the extracted data."
    },
    "ragas": {
      "ragas_faithfulness": 0.0,
      "ragas_reasoning": "Ragas Engine Error: 'GeminiDeepEvalWrapper' object has no attribute 'invoke'"
    }
  },
```
