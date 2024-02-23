# IP to ASN Mapper using CAIDA
A streamlined Python tool for mapping IP addresses to ASNs, leveraging CAIDA's pyipmeta library and CAIDA's data repository of daily RouteViews prefix-to-AS snapshots.

## Key Features:

- **CAIDA PyIPMeta Integration**: Utilizes CAIDA's pyipmeta for IP to ASN mappings.
- **Daily RouteViews Snapshots**: Utilizes daily snapshots from RouteViews' prefix-to-AS dataset.
- **Pandas Compatibility**: Easily integrates with pandas for handling large datasets efficiently.
- **Historical Analysis Support**: Offers the ability to use snapshots from specific dates for retrospective studies.

This tool simplifies the process of associating IP addresses with their corresponding Autonomous Systems. Contributions and feedback are welcome to further enhance its capabilities.

## Requirements

To use this tool, you will need Python 3.x and the following Python packages:

- requests
- beautifulsoup4
- pandas

Install these packages using pip:

```bash
pip install -r requirements.txt
```

### Additional External Requirements

This tool also requires the installation of `pyipmeta` and `libipmeta`, which are not available through pip. Follow the installation instructions on their respective GitHub pages:

- [pyipmeta](https://github.com/CAIDA/pyipmeta)
- [libipmeta](https://github.com/CAIDA/libipmeta)

Ensure you have these libraries installed and properly configured before running the IP to ASN Mapper.

## Usage

```bash
python map_ip_to_asn.py
```