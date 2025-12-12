from tensorflow.keras import layers, models

def build_autoencoder(input_dim, latent_dim=8):
    inp = layers.Input(shape=(input_dim,))
    x = layers.Dense(max(32, input_dim*2), activation="relu")(inp)
    x = layers.Dense(max(16, input_dim), activation="relu")(x)
    latent = layers.Dense(latent_dim, activation="relu")(x)
    x = layers.Dense(max(16, input_dim), activation="relu")(latent)
    x = layers.Dense(max(32, input_dim*2), activation="relu")(x)
    out = layers.Dense(input_dim, activation="linear")(x)
    model = models.Model(inp, out)
    return model