# **pgvector Benchmarking Suite**

## **Project Overview**
This project benchmarks **pgvector performance** in **PostgreSQL** under **semantic similarity workloads**.  
It evaluates:
- **Indexing strategies:** `IVFFlat`, `HNSW`, and `No Index`
- **Dimensionality impact:** `128D`, `256D`, `512D`
- **Dataset sizes:** `500K`, `1M`, `5M`
- **Query loads:** Various concurrency levels

## **Setup Instructions**
### **Deploy PostgreSQL VMs**
Two **base VMs** are created, one for `pgvector` and the other for load generation.
Additional **server and client VMs** are cloned from these bases using `create_vms_from_snapshot.py`.

To create VMs:
```bash
python create_vms_from_snapshot.py
```
- PostgreSQL runs on **3 VMs** for different dimensions (`128D`, `256D`, `512D`).
- Uses **Google Cloud Compute Engine** with `e2-standard-8` instances.
- Additional **client VMs** are created with `e2-small` instances to generate query loads.

---

### **Install Dependencies**
Ensure **Python 3.x** is installed. Then run:
```bash
pip install -r requirements.txt
```
Ensure **PostgreSQL** with **pgvector** is installed.
Ensure **pg_hba.conf** is correctly updated with the load generator IPs.

---

### **Generate Data & Indexes**
Run:
```bash
python run_data_generator.py
```
- Populates datasets (`500K`, `1M`, `5M` embeddings).
- Creates **IVFFlat & HNSW indexes**.

---

## **Running Benchmarks**
The benchmarking suite evaluates:
- The **impact of indexing (`No Index`, `IVFFlat`, `HNSW`) on query latency**.
- **Throughput variations** under different concurrency levels (10, 50, 100+ clients).
- **Scalability trends** as dataset sizes increase (500K → 1M → 5M embeddings).

To execute the benchmark inside the **Client VM**, run:
```bash
python run_benchmark.py
```
- Reads configuration from `config.json`
- Benchmarks each table across **different concurrency levels** and **number of queries**.
- Stores logs in `results/`

---

## **Example Output (Benchmark Results)**
Results are stored in CSV format inside `results/`.  
Each row represents a benchmark result for a table with a specific indexing strategy and dataset size.

### **Key Columns Explained:**
| Column Name | Description |
|-------------|------------|
| `table_name` | Table being benchmarked (index type + dimension + dataset size) |
| `num_queries` | Number of queries executed |
| `num_clients` | Number of concurrent clients |
| `avg_latency` | Average time taken per query (seconds) |
| `p50_latency` | 50th percentile (median) latency |
| `p90_latency` | 90th percentile latency |
| `p99_latency` | 99th percentile latency (worst-case scenarios) |
| `throughput` | Queries executed per second (not counting the time between two queries) |
| `elapsed_time` | Total time taken for benchmark run |

---

## **Visualizing Results**
To generate performance charts put the results in **visualize_results**
```bash
python visualizer.py
```
### **Charts Included:**
- **Latency Trends:** P50, P90, P99 latencies across index types.
- **Throughput Comparisons:** Queries per second by dataset size.
- **Dimensionality Trade-offs:** Scaling impact of 128D, 256D, 512D.
- **Scalability Impact:** How dataset size affects performance.
- **Throughput vs. Latency Analysis:** Direct comparison of performance.

---

## **Troubleshooting**
### **Benchmarking script crashes or fails to connect to PostgreSQL**
- Ensure that **PostgreSQL is running** on the correct VM and accepting connections.
    ```bash
    sudo systemctl status postgresql
    ```
- Check the **pg_hba.conf** file to allow external connections.
- Check if the experiment and database configurations in **Client/config.json** are correct.

### **Visualizations are empty or incorrect**
- Make sure that the `results/` directory contains the benchmark output files before running `visualizer.py`.
