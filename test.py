import tensorflow as tf
import numpy as np

# Generate a sample sequence
sequence = np.array([12, 34, 56, 78, 90, 11, 23, 45, 67, 89])

# Prepare the data for training
X = sequence[:-1].reshape(-1, 1, 1) # input sequence, shape=(batch_size, seq_length, input_dim)
y = sequence[1:].reshape(-1, 1) # target sequence, shape=(batch_size, seq_length)

# Define the model architecture
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(64, input_shape=(1, 1)),
    tf.keras.layers.Dense(1)
])

# Compile the model
model.compile(loss='mean_squared_error', optimizer='adam')

# Train the model
model.fit(X, y, epochs=100)

# Predict the next number
next_number = model.predict(np.array([[sequence[-1]]]).reshape(-1, 1, 1))
print(f"The next number is {next_number[0][0]:.0f}")
