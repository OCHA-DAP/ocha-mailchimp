# Installation

## From PyPI

Install ocha-mailchimp using pip:

```bash
pip install ocha-mailchimp
```

## Development Installation

For development, install from source:

1. Clone the repository:
```bash
git clone https://github.com/OCHA-DAP/ocha-mailchimp.git
cd ocha-mailchimp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Environment Configuration

Create a `.env` file in your project root:

```bash

DSCI_AZ_BLOB_DEV_SAS=your_dev_sas_token

```

## Dependencies

ocha-mailchimp requires Python 3.10 or later and depends on:


These will be installed automatically when you install ocha-mailchimp.
