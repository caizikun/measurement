config = {}


config['waveplates_lt3'] = {
	
	'zpl_half': {
		'channel' : 1,
		'axis'	  : 1,
		'pos_calib_quick' : 639,#steps/degree
		'pos_calib_precise': 893,
		'neg_calib_quick' : 806,#steps/degree
		'neg_calib_precise': 1527,
	},
	'zpl_quarter': {
		'channel' : 1,
		'axis'	  : 2,
		'pos_calib_quick' : 613,#steps/degree
		'pos_calib_precise': 826,
		'neg_calib_quick' : 421,#steps/degree
		'neg_calib_precise': 1389,
	},
	'cryo_half': {
		'channel' : 2,
		'axis'	  : 1,
		'pos_calib_quick' : 514,#steps/degree
		'pos_calib_precise': 617,
		'neg_calib_quick' : 457,#steps/degree
		'neg_calib_precise': 784,
	},
}

config['waveplates_lt1'] = {
	
	'zpl_half': {
		'channel' : 1,
		'axis'	  : 2,
		'pos_calib_quick' : 500,#steps/degree
		'pos_calib_precise': 478,
		'neg_calib_quick' : 432,#steps/degree
		'neg_calib_precise': 474,
	},
	'zpl_quarter': {
		'channel' : 2,
		'axis'	  : 1,
		'pos_calib_quick' : 510,#steps/degree
		'pos_calib_precise': 500,
		'neg_calib_quick' : 500,#steps/degree
		'neg_calib_precise': 500,
	},
		'cryo_half': {
		'channel' : 2,
		'axis'	  : 2,
		'pos_calib_quick' : 510,#steps/degree
		'pos_calib_precise': 833,
		'neg_calib_quick' : 500,#steps/degree
		'neg_calib_precise': 714,
	},
}