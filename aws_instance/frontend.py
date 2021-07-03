
import click

from aws_instance.backend import Config

# load the configuration file.
config = Config.load()


@click.group()
def main():
    """Manage AWS EC2 instances"""
    pass


@main.command()
def list():
    """List instance statuses"""
    max_len = max(map(len, config.names))
    for name, state in zip(config.names, config.states):
        pad = " " * (max_len - len(name))
        print(f"{name}: {pad}{state}")


@main.command()
@click.argument("name", type=click.Choice(config.names))
def start(name: str):
    """Start an instance"""
    (prev, curr) = config.start(name)
    print(f"{name}: {prev} -> {curr}")


@main.command()
@click.argument("name", type=click.Choice(config.names))
def stop(name: str):
    """Stop an instance"""
    (prev, curr) = config.stop(name)
    print(f"{name}: {prev} -> {curr}")


@main.command()
@click.argument("name", type=click.Choice(config.names))
def ssh(name: str):
    """Log into an instance"""
    config.ssh(name)


@main.command()
@click.argument("name", type=click.Choice(config.names))
@click.option(
    "-p", "--port",
    type=int,
    default=config.default_port,
    show_default=True,
    help="Port number",
)
def tunnel(name: str, port: int):
    """Open a tunnel to an instance"""
    config.tunnel(name, port)


if __name__ == "__main__":
    main()
