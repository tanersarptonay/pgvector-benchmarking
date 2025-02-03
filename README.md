# **pgvector Benchmarking Suite**

## **Project Overview**
This project benchmarks **pgvector performance** in **PostgreSQL** under **semantic similarity workloads**.  
It evaluates:
- **Indexing strategies:** `IVFFlat`, `HNSW`, and `No Index`
- **Dimensionality impact:** `128D`, `256D`, `512D`
- **Dataset sizes:** `1M`, `5M`, `10M`
- **Query loads:** Various concurrency levels

## **Setup Instructions**
### **Deploy PostgreSQL VMs**
Two **base VMs** are created for for `pgvector` and load generation.
Additional **server and client VMs** are cloned from these bases using `create_vms_from_snapshot.py`.

To create VMs:
```bash
python create_vms_from_snapshot.py
```
- PostgreSQL runs on **3 VMs** for different dimensions (`128D`, `256D`, `512D`).
- Uses **Google Cloud Compute Engine** with `e2-standard-4` instances.
- Additional **client VMs** are created to generate query loads.

---

### **Install Dependencies**
Ensure **Python 3.x** is installed. Then run:
```bash
pip install -r requirements.txt
```
Ensure **PostgreSQL with pgvector** is installed.

---

### **Generate Data & Indexes**
Run:
```bash
python run_data_generator.py
```
- Populates datasets (1M, 5M, 10M embeddings).
- Creates **IVFFlat & HNSW indexes**.

---

## **Running Benchmarks**
To execute the benchmarking suite:
```bash
python run_benchmark.py
```
- Reads configuration from `config.json`
- Benchmarks each table across **different concurrency levels**
- Stores logs in `results/`

---

## **Example Output (Benchmark Results)**
Results are stored in CSV format inside `results/`.  
Here’s an example result:

```
table_name,num_queries,num_clients,avg_latency,min_latency,max_latency,p50_latency,p90_latency,p95_latency,p99_latency,stddev_latency,throughput,success_rate,failure_rate,elapsed_time
items_no_index_128_1M,5000,10,1.493,0.145,5.742,1.447,1.546,2.406,3.232,0.384,0.669,100.0,0.0,747.549
items_ivfflat_128_1M,5000,10,0.044,0.025,0.151,0.044,0.047,0.049,0.081,0.007,22.240,100.0,0.0,22.600
items_hnsw_128_1M,5000,10,0.040,0.020,0.146,0.038,0.045,0.057,0.076,0.008,24.814,100.0,0.0,20.264
```

To visualize results:
```bash
python analyze_results.py
```
- **Latency Trends:** P50, P90, P99 latencies across index types.
- **Throughput Comparisons:** Queries per second by dataset size.
- **Dimensionality Trade-offs:** Scaling impact of 128D, 256D, 512D.

---