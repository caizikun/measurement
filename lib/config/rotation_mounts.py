config = {}


config['waveplates_lt3'] = {
	
	'zpl_half': {
		'channel' : 1,
		'axis'	  : 1,
		'pos_calib_quick' : 752,#steps/degree
		'pos_calib_precise': 1000,#992 ,
		'neg_calib_quick' : 430 ,#steps/degree
		'neg_calib_precise': 1000,#1527,
	},
	'zpl_quarter': {
		'channel' : 1,
		'axis'	  : 2,
		'pos_calib_quick' :701,#steps/degree
		'pos_calib_precise': 1000,#826,
		'neg_calib_quick' : 991,#steps/degree
		'neg_calib_precise': 1000,#1158,
	},
	'cryo_half': {
		'channel' : 2,
		'axis'	  : 1,
		'pos_calib_quick' :527 ,#steps/degree
		'pos_calib_precise': 771 ,
		'neg_calib_quick' :481 ,#steps/degree
		'neg_calib_precise':1120 ,
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
config['waveplates_lt4'] = {
	
	'zpl_half': {
		'channel' : 1,
		'axis'	  : 1,
		'pos_calib_quick' : 523,#steps/degree
		'pos_calib_precise': 744,
		'neg_calib_quick' : 448 ,#steps/degree
		'neg_calib_precise':763,
	},
	'zpl_quarter': {
		'channel' : 1,
		'axis'	  : 2,
		'pos_calib_quick' : 672,#steps/degree
		'pos_calib_precise':826,
		'neg_calib_quick' : 401,#steps/degree
		'neg_calib_precise':800,#1068,
	},
		'cryo_half': {
		'channel' : 2,
		'axis'	  : 1,
		'pos_calib_quick' : 420,#steps/degree
		'pos_calib_precise': 726,
		'neg_calib_quick' : 405,#steps/degree
		'neg_calib_precise': 747,
	},
}