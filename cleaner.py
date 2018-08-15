import dax
import pandas


class XnatSubject:
    
    def __init__(self, subject_label, database='CUTTING', xnat=None):
        "Initialize subject and connections to XNAT."
        
        self.subject = subject_label
        self.database = database
        
        # Create XNAT interface if not provided
        if xnat is None:
            xnat = dax.XnatUtils.get_interface()
        self.interface = xnat
        
        # Select XNAT object
        self.xnat_object = xnat.select.project(database).subject(subject_label)
        
        # Populate metadata for subject
        self.get_metadata()
    
    
    def get_metadata(self):
        "Return information about the subject's sessions and scans."
        
        # Get data on the individual session
        session_data = dax.XnatUtils.list_sessions(self.interface, 
                                                   self.database, 
                                                   self.subject)
        sess_df = pandas.DataFrame(session_data)
        
        # Get data on each individual scan
        scan_data = []
        for ii, sess in sess_df.iterrows():
            scan_data += dax.XnatUtils.list_scans(self.interface, 
                             self.database, self.subject, sess['label'])
        scan_df = pandas.DataFrame(scan_data)
        
        # Throw error if there is more than one session available
        if len(session_data) != 1:
            raise ValueError('This subject has too many sessions in XNAT. Please combine them.')

        self.meta = {'project': self.subject[0:3],
                     'nsessions': len(session_data),
                     'session_date': sess_df['date'].tolist(), 
                     'session_id': sess_df['ID'].tolist(),
                     'session_label': sess_df['label'].tolist(),
                     'subject_id': sess_df['subject_ID'].tolist(),
                     'scan_list': scan_df.apply(lambda x: )
                    }
        self.session_df = sess_df
        self.scan_df = scan_df


    def match_and_update_scan_types(self, overwrite=False):
        "Match scans from self.scan_df to the repository of possible scan renames."

        rename_dict = self.get_scan_rename_dict(project=self.meta['project'])
        
        for _, scan in self.scan_df.iterrows():
            scan_tuple = (scan.series_description, scan.scan_type)
            if scan_tuple in rename_dict.keys():
                new_type = rename_dict[scan_tuple]

                # Update the attribute on XNAT, if overwrite is selected
                if overwrite = True:
                    self.interface.select(scan.ID).attrs.set('scan_type', new_type)


    def get_scan_rename_dict(self, project=None):
        """Generate a dictionary of (series_description, scan_type) pairs that encode a 
        valid renaming instance. Dicionary is ndexed by project."""

        if project is None:
            raise ValueError('No project was selected.')

        rename_dict = {
            'RC3': {
                ('t1_structural', 't1_structural'): 't1_improved3d',
                ('pass1_an', 'pass1_an'): 'rc3_pass_an1'
            }
        }

        if project is not None:
            return rename_dict[project]