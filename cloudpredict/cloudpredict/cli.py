import click
import json
from .predict import predict_latency

@click.group()
def cli():
    """CloudPredict — serverless migration forecaster"""
    pass

@cli.command()
@click.option('--source', required=True,
              type=click.Choice(['aws','azure','gcp']))
@click.option('--target', required=True,
              type=click.Choice(['aws','azure','gcp']))
@click.option('--exec-mean', required=True, type=float,
              help='Mean execution time on source (ms)')
@click.option('--mem-mean', required=True, type=float,
              help='Mean memory usage on source (MB)')
@click.option('--runtime', type=click.Choice(['python','nodejs','java']),
              default='python')
def predict(source, target, exec_mean, mem_mean, runtime):
    """Predict latency after migrating to target platform."""
    result = predict_latency(source, target, exec_mean, mem_mean, runtime)
    click.echo(f"\n📊 Migration forecast: {source.upper()} → {target.upper()}")
    click.echo(f"   Predicted latency : {result['latency_ms']:.0f} ms")
    click.echo(f"   95th percentile   : {result['p95_ms']:.0f} ms")
    click.echo(f"   Estimated cost    : ${result['cost_usd']:.6f} per invoke\n")

if __name__ == '__main__':
    cli()
