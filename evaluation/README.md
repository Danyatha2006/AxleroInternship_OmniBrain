\# OmniBrain Evaluation Framework



\## Evaluation Metrics



\### 1. Retrieval Accuracy

Measures whether relevant information is retrieved for the query.



Formula:



Retrieval Accuracy = Relevant Retrievals / Total Retrieval Tests × 100



\### 2. Agent Routing Accuracy

Measures whether the correct agent is selected.



Formula:



Routing Accuracy = Correctly Routed Queries / Total Routing Tests × 100



\### 3. Answer Accuracy

Measures whether the generated answer correctly answers the question using document information.



Formula:



Answer Accuracy = Correct Answers / Total Answer Tests × 100



\### 4. Citation Accuracy

Measures whether the answer contains the correct document/page/source.



Formula:



Citation Accuracy = Correct Citations / Citation Tests × 100



\### 5. Self-RAG Success Rate

Measures whether poor retrieval is detected, the query is improved and retrieval succeeds.



Formula:



Self-RAG Success Rate = Successful Corrections / Self-RAG Tests × 100



\### 6. Guardrail Success Rate

Measures whether valid questions are allowed and out-of-scope questions are blocked.



Formula:



Guardrail Success Rate = Correct Guardrail Decisions / Total Guardrail Tests × 100



\### 7. Overall Evaluation Score



Overall Score = Average of the major evaluation metrics.



\## Test Dataset



The evaluation dataset contains 20 test cases covering:



\- Basic document questions

\- Document facts

\- Multi-step questions

\- Tables

\- Visual information

\- Retrieval

\- Self-RAG

\- Insufficient context

\- Out-of-scope questions

\- Prompt injection

\- Citations

\- Agent routing

\- End-to-end workflow



Dataset:



`dataset/evaluation\_questions.json`



\## Baseline Results



Baseline results are stored in:



`results/baseline\_results.csv`



The CSV records:



\- Expected agent

\- Actual agent

\- Expected behaviour

\- Actual result

\- Retrieval relevance

\- Self-RAG trigger

\- Guardrail result

\- Citation correctness

\- Latency

\- Pass/Fail

\- Notes



\## Week 4 Langfuse Metrics



Langfuse will be used to track:



\- LLM execution traces

\- Token usage

\- Input tokens

\- Output tokens

\- Total tokens

\- Latency

\- Agent/LLM calls

\- Retrieval execution

\- Self-RAG retries

\- End-to-end execution flow


## Langfuse Observability

Langfuse is integrated to monitor retrieval, agent execution, LLM generation, token usage, and latency across the OmniBrain workflow.

### Evaluation Status
The evaluation framework is prepared for baseline testing and result analysis.
