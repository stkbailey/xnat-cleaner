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
                     'subject_id': sess_df['subject_ID'].tolist()
                    }
        self.session_df = sess_df
        self.scan_df = scan_df
