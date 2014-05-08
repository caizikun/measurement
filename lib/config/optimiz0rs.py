dimension_sets = {
            'lt2': {
                'x' : {
                    'scan_length' : 1.5,
                    'nr_of_points' : 31,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.0,
                    'nr_of_points' : 31,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 4.,
                    'nr_of_points' : 31,
#                    'pixel_time' : 50,
                    },
                'zyx' : ['z','y','x'],
                'xyonly':['y','x'],
                },
            
            'lt1' : {
                'x' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 2.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'zyx' : ['z','y','x'],
                'xyonly':['y','x'],
                },

            'lt3' : {
                'x' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 4.,
                    'nr_of_points' : 51,#99,
#                    'pixel_time' : 50,
                    },
                'zyx' : ['z','y','x'],
                'xyonly':['y','x'],
                },

            'rt2' : {
                'x' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 4.,
                    'nr_of_points' : 51,#99,
#                    'pixel_time' : 50,
                    },
                'zyx' : ['z','y','x'],
                'xyonly':['y','x'],
                },

            }