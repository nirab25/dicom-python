# DICOM Tools

A Python utility for working with DICOM files and servers, specifically focused on Modality Worklist (MWL) functionality.

## Overview

This tool provides two main functions:

1. **Converting MWL sample files to DICOM format**: Converts text-based MWL sample files to DICOM (.dcm) files that can be used for testing and development.
2. **Testing connectivity with DICOM servers using C-ECHO**: Verifies connectivity with DICOM servers by performing a C-ECHO operation.

## Prerequisites

- Python 3.7 or later
- Required Python packages (install using `pip install -r requirements.txt`):
  - pydicom
  - pynetdicom
  - requests

## Installation

1. Clone this repository or download the script.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

The script can be run with various command-line options:

```bash
python dicom_tools.py [options]
```

### Available Options

- `--convert`: Convert MWL sample files to DICOM format
- `--echo`: Test connectivity with a DICOM server using C-ECHO
- `--server-ip`: IP address of the DICOM server (default: 10.10.0.1)
- `--server-port`: Port of the DICOM server (default: 4242)
- `--server-ae`: AE title of the DICOM server (default: MERCURE)
- `--client-ae`: AE title of the client (default: BEXA)
- `--verbose`, `-v`: Enable verbose output
- `--help`, `-h`: Show help message and exit

### Examples

#### Converting MWL Sample Files to DICOM Format

```bash
python dicom_tools.py --convert
```

This will:
1. Read the MWL sample text files from the `data/mwl-sample/` directory
2. Convert them to DICOM (.dcm) files
3. Save the DICOM files to the `data/mwl-sample/dcm/` directory

#### Testing Connectivity with a DICOM Server

```bash
python dicom_tools.py --echo
```

This will:
1. Establish a DICOM association with the server
2. Send a C-ECHO request
3. Print the response from the server

#### Custom Server Configuration

```bash
python dicom_tools.py --echo --server-ip 192.168.1.100 --server-port 104 --server-ae ORTHANC --client-ae CLIENT
```

#### Enabling Verbose Output

```bash
python dicom_tools.py --echo --verbose
```

## File Structure

- `dicom_tools.py`: The main script containing all functionality
- `data/mwl-sample/`: Directory containing sample MWL files
  - `DMWL - Query Request.txt`: Sample MWL request file
  - `DMWL - Query Response.txt`: Sample MWL response file
  - `dcm/`: Directory containing converted DICOM files
    - `mwl_request.dcm`: Converted MWL request file
    - `mwl_response.dcm`: Converted MWL response file

## Functions

### `convert_mwl_samples()`

Converts MWL sample text files to DICOM (.dcm) files.

### `c_echo(ip_address, port, remote_ae, local_ae)`

Performs a C-ECHO operation with a DICOM server.

Parameters:
- `ip_address`: IP address of the DICOM server
- `port`: Port of the DICOM server
- `remote_ae`: AE title of the remote DICOM server
- `local_ae`: AE title of the local DICOM client

Returns:
- Status code from the C-ECHO response (0 indicates success)

## Troubleshooting

### Connection Issues

If you encounter connection issues with the DICOM server:

1. Verify that the server is running and accessible
2. Check that the IP address, port, and AE titles are correct
3. Ensure that the server supports the Verification SOP Class (for C-ECHO)
4. Check firewall settings to ensure the port is open

### Conversion Issues

If you encounter issues with the MWL sample file conversion:

1. Verify that the sample files exist in the `data/mwl-sample/` directory
2. Check that the sample files have the expected format
3. Ensure that the output directory (`data/mwl-sample/dcm/`) is writable

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [pydicom](https://github.com/pydicom/pydicom) - Python package for working with DICOM files
- [pynetdicom](https://github.com/pydicom/pynetdicom) - Python implementation of the DICOM networking protocol
