

import numpy as np
import qt
import measurement.lib.measurement2.measurement as m2
import measurement.lib.measurement2.qutau.qutau_measurement as qm

reload(qm)

qutau=qt.instruments['QuTau']

# SAMPLE = qt.exp_params['samples']['current']
# SAMPLE_CFG = qt.exp_params['protocols']['current']


def self_test(name):
	"stuff goes in here"
	m = qm.qutau_measurement(name)
	m.autoconfig()
	out= qutau.configure_selftest(np.array([0]),500e-9,3,10e-6) #([list of channels], period, burst_periods, burst_distance) see instrument driver.
	print 'qutau error code: ', out
	m.run()


if __name__ == '__main__':

	self_test('testing')
