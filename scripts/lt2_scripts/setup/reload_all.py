# put everything in here that needs to be updated when changed

# reload adwin
import qt
import measurement.lib.config.adwins as adwins_cfg
reload(adwins_cfg)
# adwin = qt.instruments['adwin']
# reload(adwins_cfg)
# qt.instruments.reload(adwin)

# reload AWG channel config and pulsar config

from measurement.lib.pulsar import pulse, element, pulsar, pulselib, eom_pulses
reload(pulse)
reload(element)
reload(pulsar)
reload(pulselib)
reload(eom_pulses)

# measurement classes
from measurement.lib.measurement2 import measurement
reload(measurement)

from measurement.lib.measurement2.pq import pq_measurement
reload(pq_measurement)

from measurement.lib.measurement2.adwin_ssro import ssro
reload(ssro)

# pulsar measurements
from measurement.lib.measurement2.adwin_ssro import pulsar_msmt
reload(pulsar_msmt)

from measurement.lib.measurement2.adwin_ssro import pulsar_mbi_espin
reload(pulsar_mbi_espin)

# from measurement.scripts.lt2_scripts.setup import msmt_params as mcfg
# reload(mcfg)

from measurement.lib.measurement2.adwin_ssro import pulsar_delay
reload(pulsar_delay)

from measurement.lib.measurement2.adwin_ssro import pulsar_pq
reload(pulsar_pq)
from measurement.lib.measurement2.adwin_ssro import dynamicaldecoupling
reload(dynamicaldecoupling)

from measurement.lib.measurement2.adwin_ssro import DD_2; reload(DD_2)

from measurement.lib.measurement2.adwin_ssro import pulse_select as ps 
reload(ps)

