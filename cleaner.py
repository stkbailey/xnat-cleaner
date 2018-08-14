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
        sess_dict = session_data[0]
        
        # Throw error if there is more than one session available
        if len(session_data) != 1:
            raise ValueError('This subject has too many sessions in XNAT. Please combine them.')
                
        self.meta = {'project': self.subject[0:3],
                     'nsessions': len(session_data),
                     'session_date': sess_dict['date'], 
                     'session_id': sess_dict['ID'],
                     'session_label': sess_dict['label'],
                     'subject_id': sess_dict['subject_ID']
                    }
