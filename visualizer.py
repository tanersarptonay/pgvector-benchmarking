import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_latency_heatmap(df):
    """Generates a heatmap for average latency comparisons across indexing strategies and dataset sizes."""
    plt.figure(figsize=(8, 6))
    df_agg = df.groupby(["dataset_size", "indexing_type"], as_index=False).agg({"avg_latency": "mean"})
    pivot_latency = df_agg.pivot(index="dataset_size", columns="indexing_type", values="avg_latency")
    sns.heatmap(pivot_latency, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.xlabel("Indexing Strategy")
    plt.ylabel("Dataset Size (Rows)")
    plt.title("Average Latency by Indexing Strategy and Dataset Size")
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


def plot_throughput_vs_indexing(df):
    """Generates a bar chart comparing query throughput across indexing strategies and dataset sizes."""
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x="indexing_type", y="throughput", hue="dataset_size", palette="pastel")
    plt.xlabel("Indexing Strategy")
    plt.ylabel("Corrected Query Throughput (queries/sec)")
    plt.title("Corrected Query Throughput Across Indexing Strategies")
    plt.legend(title="Dataset Size")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()


def plot_scalability(df):
    """Generates a line chart showing how latency scales with dataset size for each indexing strategy."""
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dataset_size", y="avg_latency", hue="indexing_type", marker="o", palette="Dark2")
    plt.xlabel("Dataset Size (Rows)")
    plt.ylabel("Average Latency (s)")
    plt.title("Scalability: Dataset Size vs. Latency Across Indexing Strategies")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()


def plot_throughput_vs_dimension(df):
    """Generates a line chart showing query throughput across different embedding dimensions for each indexing strategy."""
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dimension", y="throughput", hue="indexing_type", marker="o", palette="Dark2")
    plt.xlabel("Embedding Dimensionality")
    plt.ylabel("Query Throughput (queries/sec)")
    plt.title("Throughput Across Different Embedding Dimensions")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()


def plot_throughput_vs_dataset_size(df):
    """Generates a line chart showing query throughput across different dataset sizes for each indexing strategy."""
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x="dataset_size", y="throughput", hue="indexing_type", marker="o", palette="Set1")
    plt.xlabel("Dataset Size (Rows)")
    plt.ylabel("Query Throughput (queries/sec)")
    plt.title("Throughput Across Different Dataset Sizes")
    plt.legend(title="Indexing Strategy")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()

