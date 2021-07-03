
import os
import yaml
import functools
import subprocess

import boto3.ec2
from botocore.exceptions import ClientError

from typing import Dict, List, Tuple
from dataclasses import dataclass

# use a global EC2 handle.
ec2 = boto3.client("ec2")


def run(command) -> Dict:
    """Execute a command after an initial dry-run"""
    try:
        command(DryRun=True)
    except ClientError as err:
        if "DryRunOperation" not in str(err):
            raise

    return command(DryRun=False)


def start(ids: List[str]):
    """Start one or more instances"""
    return functools.partial(ec2.start_instances, InstanceIds=ids)


def stop(ids: List[str]):
    """Stop one or more instances"""
    return functools.partial(ec2.stop_instances, InstanceIds=ids)


def describe(ids: List[str]):
    """Describe one or more instances"""
    return functools.partial(ec2.describe_instances, InstanceIds=ids)


@dataclass(frozen=True)
class Instance:
    name: str
    inst_id: str

    @property
    def address(self) -> str:
        """IP Address"""
        response = run(describe(ids=[self.inst_id]))

        for res in response["Reservations"]:
            inst_info = res["Instances"][0]
            if inst_info["InstanceId"] == self.inst_id:
                return inst_info["PublicIpAddress"]

    def start(self) -> Tuple[str, str]:
        """Start the instance"""
        response = run(start(ids=[self.inst_id]))
        prev = response["StartingInstances"][0]["PreviousState"]["Name"]
        curr = response["StartingInstances"][0]["CurrentState"]["Name"]
        return (prev, curr)

    def stop(self) -> Tuple[str, str]:
        """Stop the instance"""
        response = run(stop(ids=[self.inst_id]))
        prev = response["StoppingInstances"][0]["PreviousState"]["Name"]
        curr = response["StoppingInstances"][0]["CurrentState"]["Name"]
        return (prev, curr)


@dataclass(frozen=True)
class Config:
    ident: str
    username: str
    instances: Dict[str, str]
    default_port: int = 9999

    def __len__(self) -> int:
        """Number of instances"""
        return len(self.instances)

    def __iter__(self):
        """Iterate over the instances"""
        return iter(self.instances.items())

    def __contains__(self, name: str) -> bool:
        """Check if an instance name is supported"""
        return name in self.instances

    def __getitem__(self, name: str) -> Instance:
        """Get an instance"""
        return Instance(name, self.instances[name])

    def start(self, name: str) -> Tuple[str, str]:
        """Start an instance"""
        return self[name].start()

    def stop(self, name: str) -> Tuple[str, str]:
        """Stop an instance"""
        return self[name].stop()

    def ssh(self, name: str):
        """Start a shell on an instance"""
        ip = self[name].address
        subprocess.run([
            "ssh", "-i", self.ident,
            f"{self.username}@{ip}",
        ])

    def tunnel(self, name: str, port: int):
        """Connect to a port on the instance"""
        ip = self[name].address
        subprocess.run([
            "ssh", "-i", self.ident, "-N", "-L",
            f"{port}:localhost:{port}",
            f"{self.username}@{ip}",
        ])

    @property
    def names(self) -> Tuple[str, ...]:
        """Supported instance names"""
        return tuple(self.instances.keys())

    @property
    def instance_ids(self) -> Tuple[str, ...]:
        """Suported instance ids"""
        return tuple(self.instances.values())

    @property
    def states(self) -> Tuple[str, ...]:
        """Instance statuses"""
        response = run(describe(ids=list(self.instance_ids)))

        states = []
        for name, inst_id in self:
            for res in response["Reservations"]:
                inst_info = res["Instances"][0]
                if inst_info["InstanceId"] == inst_id:
                    state = inst_info["State"]["Name"]
                    states.append(state)

        return tuple(states)

    @classmethod
    def load(cls):
        """Instantiate a Config from its yaml source"""
        filename = os.path.join(
            os.path.expanduser("~"),
            ".config",
            "aws-instance.yaml",
        )

        with open(filename, "rt", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)

        return cls(**config)
