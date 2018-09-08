# Xnat Cleaner
The purpose of this package is to update the Cutting lab's data on XNAT so that it remains consistent and appropriately named. This allows assessors to be run on the data in a timely fashion, and promots analyses by alerting users to inappropriate data

        # Create metadata, specially around the project and the scan series description
        # We will compare the scan to a list of suggested renames, then rename it if appropriate.
        
## Usage
To run a subject through the cleaner, do the following:

```
from cleaner import XnatSubject
x = XnatSubject('LD4001_v1')
```
This instantiates a new subject and does the following:

1. Retrieves subject information from Xnat and dumps it into `x.meta`, `x.session_df` and `x.scan_df`.
2. Checks for scans that might be eligible for renaming.
	a. To update scan types, call `x.update_scan_types(overwrite=True)`.
3. Tests for common errors, such as duplicate scans or incomplete scans.
	a. To rename "incomplete scans", call `x.update_incomplete_scan_types()`. (Future update)
4. Prints a summary of the scan to the screen. 

#### Sources of error
- All subjects should match the RegEx pattern: '[A-Z]{2}\d{4}_v[A-Z0-9]' (e.g. LD4001_v1)

#### Future improvements
- Create an `update_incomplete_scan_types()` function to change incomplete scans to "incomplete".
- Check if the scan quality is consistent with expectatinos (e.g. same amount of frames), file size, etc.
