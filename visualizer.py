import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_latency_heatmap_size(df):
    """Generates a heatmap for average latency comparisons across indexing strategies and dataset sizes."""
    plt.figure(figsize=(8, 6))
    df_agg = df.groupby(["dataset_size", "indexing_type"], as_index=False).agg({"avg_latency": "mean"})
    pivot_latency = df_agg.pivot(index="dataset_size", columns="indexing_type", values="avg_latency")
    sns.heatmap(pivot_latency, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.xlabel("Indexing Strategy")
    plt.ylabel("Dataset Size (Rows)")
    plt.title("Average Latency by Indexing Strategy and Dataset Size")
    plt.show()

def plot_latency_heatmap_dims(df):
    """Generates a heatmap for average latency comparisons across indexing strategies and dataset sizes."""
    plt.figure(figsize=(8, 6))
    df_agg = df.groupby(["dimension", "indexing_type"], as_index=False).agg({"avg_latency": "mean"})
    pivot_latency = df_agg.pivot(index="dimension", columns="indexing_type", values="avg_latency")
    sns.heatmap(pivot_latency, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.xlabel("Indexing Strategy")
    plt.ylabel("Dimensions")
    plt.title("Average Latency by Indexing Strategy and Dimensions")
    plt.show()


def plot_latency_vs_dimension(df):
    """Generates a line chart comparing latency across different embedding dimensions for each indexing strategy."""
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dimension", y="avg_latency", hue="indexing_type", marker="o", palette="Dark2")
    plt.xlabel("Embedding Dimensionality")
    plt.ylabel("Average Latency (s)")
    plt.title("Impact of Embedding Dimensionality on Latency")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()


def plot_latency_distribution(df):
    """Generates a boxplot showing latency distributions (p50, p90, p95, p99) for each indexing strategy."""
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="indexing_type", y="p99_latency", hue="dataset_size", palette="Set2")
    plt.xlabel("Indexing Strategy")
    plt.ylabel("p99 Latency (s)")
    plt.title("Latency Distribution Across Indexing Strategies")
    plt.legend(title="Dataset Size")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()


def plot_latency_distribution_only_index(df):
    """Generates a boxplot showing latency distributions (p50, p90, p95, p99) for each indexing strategy."""
    df = df[df["indexing_type"].isin(["IVFFlat", "HNSW"])]
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="indexing_type", y="p99_latency", hue="dataset_size", palette="Set2")
    plt.xlabel("Indexing Strategy")
    plt.ylabel("p99 Latency (s)")
    plt.title("Latency Distribution Across Indexing Strategies")
    plt.legend(title="Dataset Size")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()


def plot_throughput_vs_indexing(df, overall_throughput=True):
    """Generates a bar chart comparing query throughput across indexing strategies and dataset sizes.
       If overall_throughput is False, results don't include the time between queries.
    """
    thr = "overall_throughput" if overall_throughput else "throughput"
    thr_title = "Throughput" if overall_throughput else "Throughput"

    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="indexing_type", y=thr, hue="dataset_size", palette="pastel")
    plt.xlabel("Indexing Strategy")
    plt.ylabel(f"{thr_title} (queries/sec)")
    plt.title(f"{thr_title} Across Indexing Strategies")
    plt.legend(title="Dataset Size")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

def plot_latency_vs_indexing(df):
    """Generates a bar chart comparing query throughput across indexing strategies and dataset sizes.
       If overall_throughput is False, results don't include the time between queries.
    """
    df = df[df["indexing_type"].isin(["IVFFlat", "HNSW"])]
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="indexing_type", y="avg_latency", hue="dataset_size", palette="pastel")
    plt.xlabel("Indexing Strategy")
    plt.ylabel(f"Latency (sec)")
    plt.title(f"Latency Across Indexing Strategies")
    plt.legend(title="Dataset Size")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

def plot_scalability(df):
    """Generates a line chart showing how latency scales with dataset size for each indexing strategy."""
    df = df[df["indexing_type"].isin(["IVFFlat", "HNSW", "No Index"])]
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dataset_size", y="avg_latency", hue="indexing_type", marker="o", palette="Dark2")
    plt.xlabel("Dataset Size (Rows)")
    plt.ylabel("Average Latency (s)")
    plt.title("Scalability: Dataset Size vs. Latency Across Indexing Strategies")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()


def plot_scalability_only_index(df):
    """Generates a line chart showing how latency scales with dataset size for each indexing strategy."""
    df = df[df["indexing_type"].isin(["IVFFlat", "HNSW"])]
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dataset_size", y="avg_latency", hue="indexing_type", marker="o", palette="Dark2")
    plt.xlabel("Dataset Size (Rows)")
    plt.ylabel("Average Latency (s)")
    plt.title("Scalability: Dataset Size vs. Latency Across Indexing Strategies")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()


def plot_throughput_vs_dimension(df, overall_throughput=True):
    """Generates a line chart showing query throughput across different embedding dimensions for each indexing strategy.
       If overall_throughput is False, results don't include the time between queries.
    """
    thr = "overall_throughput" if overall_throughput else "throughput"
    thr_title = "Throughput" if overall_throughput else "Throughput"
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dimension", y=thr, hue="indexing_type", marker="o", palette="Dark2")
    plt.xlabel("Embedding Dimensionality")
    plt.ylabel(f"{thr_title} (queries/sec)")
    plt.title(f"{thr_title} Across Different Embedding Dimensions")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()


def plot_throughput_vs_dataset_size(df, overall_throughput=True):
    """Generates a line chart showing query throughput across different dataset sizes for each indexing strategy.
       If overall_throughput is False, results don't include the time between queries.
    """
    thr = "overall_throughput" if overall_throughput else "throughput"
    thr_title = "Throughput" if overall_throughput else "Throughput"
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dataset_size", y=thr, hue="indexing_type", marker="o", palette="Set1")
    plt.xlabel("Dataset Size (Rows)")
    plt.ylabel(f"{thr_title} (queries/sec)")
    plt.title(f"{thr_title} Across Different Dataset Sizes")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()

