import data
import lightning
from models import encoders, decoders, bottlenecks


def build_datamodule(model_type):
    apply_noise = (model_type == 'denoising')
    datamodule = data.MNISTDataModule('../data', apply_noise=apply_noise)

    return datamodule


def build_ae(model_type, input_shape):
    latent_dim = 32
    encoder, decoder = _build_networks(model_type, input_shape, latent_dim)
    bottleneck = _build_bottleneck(model_type, latent_dim)
    ae = lightning.Autoencoder(encoder, bottleneck, decoder, lr=0.001)

    return ae


def _build_networks(model_type, input_shape, latent_dim):
    enc_dim = dec_dim = latent_dim
    if model_type == 'vae' or model_type.startswith('beta_vae'):
        enc_dim *= 2

    num_layers = 3
    if model_type == 'shallow':
        encoder = encoders.ShallowEncoder(input_shape, enc_dim)
        decoder = decoders.ShallowDecoder(dec_dim, input_shape)
    elif model_type == 'stacked':
        encoder = encoders.StackedEncoder(input_shape, num_layers, enc_dim)
        decoder = decoders.StackedDecoder(dec_dim, num_layers, input_shape)
    else:
        encoder = encoders.DenseEncoder(input_shape, num_layers, enc_dim)
        decoder = decoders.DenseDecoder(dec_dim, num_layers, input_shape)

    return encoder, decoder


def _build_bottleneck(model_type, latent_dim):
    if model_type == 'vanilla' or model_type == 'stacked' or model_type == 'denoising':
        bottleneck = bottlenecks.IdentityBottleneck()
    elif model_type == 'vae':
        bottleneck = bottlenecks.VariationalBottleneck()
    elif model_type == 'beta_vae_strict':
        bottleneck = bottlenecks.VariationalBottleneck(beta=2.)
    elif model_type == 'beta_vae_loose':
        bottleneck = bottlenecks.VariationalBottleneck(beta=0.5)
    elif model_type == 'sparse':
        bottleneck = bottlenecks.SparseBottleneck(sparsity=0.1)
    elif model_type == 'vq':
        bottleneck = bottlenecks.VectorQuantizedBottleneck(latent_dim, num_categories=512)
    else:
        raise ValueError(f'Unknown model type {model_type}.')

    return bottleneck