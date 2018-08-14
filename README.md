# xnat-cleaner
The purpose of this package is to update the Cutting lab's data on XNAT so that it remains consistent and appropriately named. This allows assessors to be run on the data in a timely fashion, and promots analyses by alerting users to inappropriate data

        # Create metadata, specially around the project and the scan series description
        # We will compare the scan to a list of suggested renames, then rename it if appropriate.
        

#### Criteria for renaming a subject label
	- All subjects should match the RegEx pattern: '[A-Z]{2}\d{4}_v[A-Z0-9]'

#### Criteria for renaming a scan type
	- Only one scan of that type in the session
	- check if the scan has "INC" or "BAD" in it
	- check if the scan and scan data has a renaming rule in a database
	- check if the scan quality is consistent with expectatinos (e.g. same amount of frames)
