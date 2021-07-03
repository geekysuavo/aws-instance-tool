
# aws-instance-tool

A super simple tool for starting, stopping, and connecting to
Amazon EC2 instances.

## Usage

Installation is managed by `setuptools`:
```bash
cd aws-instance-tool
python3 setup.py install
```

You'll need to write a `~/.config/aws-instance.yaml` file
that contains a dictionary of names and instance identifiers,
e.g.:
```yaml
ident: /path/to/amazon.pem
username: foobar
instances:
  g4dn.xl: i-00123456789abcdef
  m5.mt: i-abcdef00123456789
```

The script is then callable as `aws-instance`, e.g.:
```bash
aws-instance start g4dn.xl
```

If you would like shell completion, then add this to your `~/.bashrc`:
```bash
eval "$(_AWS_INSTANCE_COMPLETE=bash_source aws-instance)"
```

## Licensing

These sources are released under the
[MIT License](https://opensource.org/licenses/MIT). See the
[LICENSE.md](LICENSE.md) file for the complete license terms.
