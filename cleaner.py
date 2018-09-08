import dax
import pandas


class XnatSubject:
    """Extract data from XNAT associated with a single subject. Connects to XNAT using
    user's credentials (set up previously in DAX), then pulls subject information and 
    recommends updates to scan and session information.
    
    Attributes:
        subject: XNAT subject_label (e.g. LD4001_v1)
        meta: metadata dictionary associated with subject
        database: XNAT project (e.g. CUTTING)
        interface: `dax.XnatUtils` interface instance
        sess_df: Pandas DataFrame showing all subject sessions
        scan_df: Pandas DataFrame showing all subject scans

    Methods:
        get_metadata(): Extract session and scan DataFrames.
        match_scan_types(): Checks `scan_type_renames.csv` for suggested name changes.
        update_scan_types(): Applies scan type updates to XNAT scans.       
    """    
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
        self.match_scan_types()
        self.run_test_functions()

        
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
                     'subject_id': sess_df['subject_ID'].tolist()
                    }
        self.session_df = sess_df
        self.scan_df = scan_df


    def update_scan_types(self, overwrite=False):
        """
        Performs the entire scan type evaluation process. If overwrite is True,
        this function will update each object on XNAT with the suggested
        scan type rename. If False, it will simply print the suggested renames.
        """
        # loop through each item in the matched scan types and rename
        for scan_id, new_type in self.scan_renames.iteritems():
            s  = self.scan_df.loc[self.scan_df.ID == scan_id].iloc[0]
            obj = (self.interface.select.project('CUTTING')
                       .subject(s.subject_label)
                       .experiment(s.session_label)
                       .scan(scan_id) )
                    
            # Update the attribute on XNAT, if overwrite is selected
            if overwrite == True:
                obj.attrs.set('type', new_type)
                print('Updated {} ({}, {}) to new scan type: {}'.format(scan_id, 
                                      s.series_description, s.scan_type, new_type))
                
                # Refresh the scan metadata and scan_type matches
                self.get_metadata()
                self.match_scan_types()
            
            # Otherwise, just print the updated 
            else:
                print('Scan rename (suggested): {} ({}, {}) to {}.'.format(scan_id, 
                                      s.series_description, s.scan_type, new_type))

                
    def match_scan_types(self):
        """
        Match scans from self.scan_df to the repository of possible scan renames.
        Returns a dictionary of suggested "scan type" renames.
        """
        
        # Initialize dictionary of scan_renames
        rename_dict = self.get_scan_rename_dict()
        self.scan_renames = {}

        for _, scan in self.scan_df.iterrows():
            scan_tuple = (scan.series_description, scan.scan_type)
            if scan_tuple in rename_dict.keys():
                self.scan_renames[scan.ID] = rename_dict[scan_tuple]

                
    def get_scan_rename_dict(self):
        """Generate a dictionary of (series_description, scan_type) pairs that encode a 
        valid renaming instance. Top-level dicionary is indexed by EBRL project."""

        df = pandas.read_csv('scan_type_renames.csv')

        rename_dict = {}
        for ii, s in df.loc[df.project == self.meta['project']].iterrows():
            rename_dict[(s.series_description, s.scan_type)] = s.updated_scan_type

        return rename_dict       
        
        
    def run_test_functions(self):
        """Run a series of test functions on an instance of XnatSubject. These actions include:
        
        Included functions:
            check_duplicate_scans: Checking for duplicate scans
            check_incomplete_scans: Check if the scan is of type "Incomplete" or "Unusable" in it
            Check if the scan and scan data has a renaming rule in a database
            Check if the scan quality is consistent with expectations (e.g. same amount of frames)
        """

        self.log = {}         
        self.check_duplicate_scans()
        self.check_incomplete_scans()
    
    
    def check_duplicate_scans(self):
        "Check for duplicate scan names that are not allowable (i.e. not 'Incomplete')."
        duplicates = self.scan_df.loc[self.scan_df.scan_type.duplicated()]

        try: 
            assert duplicates.shape[0] == 0
            self.log['duplicates'] = None
        except AssertionError:
            self.log['duplicates'] = duplicates['scan_type'].to_string()

        
    def check_incomplete_scans(self):
        "Check for scans tagged with 'Incomplete' or 'Unusable'."
        bad_strings = ['inc', 'bad', 'incomplete']

        bad_scans = self.scan_df.scan_type.apply(lambda x: any(s in x.lower() for s in bad_strings))
        try:
            assert bad_scans.sum() == 0
            self.log['incomplete_scans'] = None
        except AssertionError:
            self.log['incomplete_scans'] = self.scan_df.loc[bad_scans==True, 'scan_type'].to_string()