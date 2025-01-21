import numpy as np

def vector_generator(dim_size, num_vectors, seed, precision=1):
    np.random.seed(seed)
    vectors = np.random.rand(num_vectors, dim_size)
    vectors = np.round(vectors, precision)
    return vectors

if __name__ == '__main__':
    vectors = vector_generator(128, 1, 1, 1).tolist()

    output_str = "INSERT INTO items (embedding) VALUES\n"
    
    for v in vectors:
        output_str += "\t('" +  str(v) + "'),\n"

    output_str = output_str[:-2] + ";"

    print(output_str)

# Output:
"""
INSERT INTO items (embedding) VALUES
('[0.5, 0.7, 0.6, 0.5, 0.4, 0.6, 0.4, 0.9, 1.0, 0.4, 0.8, 0.5, 0.6, 0.9, 0.1, 0.1, 0.0, 0.8, 0.8, 0.9, 1.0, 0.8, 0.5, 0.8, 0.1, 0.6, 0.1, 0.9, 0.5, 0.4, 0.3, 0.8, 0.5, 0.6, 0.0, 0.6, 0.6, 0.6, 0.9, 0.7, 0.4, 0.4, 0.7, 0.1, 0.7, 0.7, 0.2, 0.1, 0.3, 0.4, 0.6, 0.4, 1.0, 0.1, 0.2, 0.2, 0.7, 0.3, 0.5, 0.2, 0.2, 0.1, 0.7, 0.1, 0.2, 0.4, 0.8, 0.1, 0.8, 0.1, 1.0, 0.5, 1.0, 0.6, 0.7, 0.0, 0.3, 0.1, 0.3, 0.1, 0.3, 0.4, 0.1, 0.7, 0.6, 0.3, 0.5, 0.1, 0.6, 0.9, 0.3, 0.7, 0.1, 0.7, 0.3, 0.2, 0.6, 0.0, 0.8, 0.0, 0.7, 0.3, 0.7, 1.0, 0.2, 0.6, 0.6, 0.6, 0.2, 1.0, 0.4, 0.8, 0.7, 0.3, 0.8, 0.4, 0.9, 0.6, 0.9, 0.7, 0.7, 0.5, 1.0, 0.6, 0.4, 0.6, 0.0, 0.3]'),
('[0.7, 0.3, 0.6, 0.4, 0.1, 0.3, 0.6, 0.6, 0.6, 0.7, 0.7, 0.4, 0.9, 0.4, 0.4, 0.9, 0.8, 0.7, 0.1, 0.9, 0.7, 1.0, 0.1, 0.9, 0.2, 0.6, 0.1, 0.8, 0.8, 0.6, 0.4, 0.1, 0.7, 0.5, 0.7, 0.9, 1.0, 0.9, 0.0, 0.4, 0.7, 0.2, 0.5, 0.1, 0.2, 0.0, 0.8, 0.2, 0.3, 0.9, 0.7, 0.0, 0.2, 0.6, 0.6, 0.2, 0.9, 0.6, 0.5, 0.6, 0.7, 0.3, 0.4, 0.2, 0.2, 0.9, 0.7, 0.5, 0.2, 0.3, 0.1, 0.4, 0.3, 0.7, 0.4, 0.2, 0.0, 0.1, 0.7, 0.5, 0.5, 0.9, 1.0, 0.2, 0.7, 0.3, 0.0, 0.8, 0.3, 0.4, 0.6, 0.8, 0.6, 0.9, 0.3, 0.8, 0.2, 1.0, 0.7, 0.2, 0.9, 0.7, 0.3, 0.2, 0.5, 0.0, 0.2, 0.4, 0.4, 0.5, 0.3, 0.6, 0.9, 0.1, 0.5, 0.1, 0.7, 0.4, 0.6, 0.2, 0.1, 0.5, 0.4, 0.9, 0.8, 0.7, 0.9, 0.1]'),
('[0.6, 0.6, 1.0, 0.3, 0.2, 0.1, 0.0, 0.9, 0.7, 0.8, 0.3, 0.6, 0.1, 0.5, 1.0, 0.9, 0.3, 1.0, 0.2, 0.9, 0.9, 0.8, 0.6, 0.9, 0.3, 0.8, 0.6, 0.0, 0.3, 0.1, 1.0, 0.5, 0.5, 0.6, 0.4, 0.1, 0.8, 0.2, 0.5, 0.2, 0.1, 0.9, 1.0, 1.0, 0.9, 0.8, 0.3, 0.1, 0.4, 0.2, 0.1, 0.1, 0.7, 0.0, 0.8, 0.1, 0.1, 0.1, 0.7, 0.2, 0.4, 0.6, 0.9, 0.7, 0.3, 0.1, 0.1, 0.3, 0.3, 0.5, 0.7, 0.7, 0.3, 0.4, 0.2, 0.8, 0.1, 0.7, 0.8, 0.8, 0.3, 0.4, 0.6, 0.3, 0.4, 0.2, 0.5, 0.0, 0.8, 0.1, 0.5, 0.3, 0.6, 1.0, 0.6, 0.0, 0.4, 0.5, 0.5, 0.7, 0.3, 0.1, 0.4, 1.0, 0.2, 0.9, 0.5, 0.5, 0.9, 0.5, 0.7, 0.4, 0.9, 0.7, 0.7, 0.3, 0.8, 0.6, 0.2, 0.2, 0.8, 1.0, 0.5, 0.6, 0.9, 0.5, 1.0, 0.6]');
"""